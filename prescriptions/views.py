from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Prescription
from .serializers import PrescriptionSerializer
from invitations.models import FarmPermission
from django.utils import timezone

# --- PDF imports ---
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io


UYGULAMA_TIPI_LABELS = {
    'yapraktan': 'Yapraktan',
    'topraktan': 'Topraktan',
    'sulamayla': 'Sulamayla',
}


class PrescriptionViewSet(ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        farm_id = self.request.query_params.get('farm_id')

        if user.role == 'farmer':
            qs = Prescription.objects.filter(farm__owner=user)
        else:
            permitted_farm_ids = FarmPermission.objects.filter(
                invitation__sender=user,
                is_active=True,
                year=timezone.now().year
            ).values_list('farm_id', flat=True)
            qs = Prescription.objects.filter(farm_id__in=permitted_farm_ids)

        if farm_id:
            qs = qs.filter(farm_id=farm_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='pdf')
    def download_pdf(self, request, pk=None):
        prescription = self.get_object()
        items = prescription.items.all().order_by('sira')

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        # Özel stiller
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=4,
            fontName='Helvetica-Bold',
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#718096'),
            spaceAfter=2,
            fontName='Helvetica',
        )
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            fontName='Helvetica-Bold',
        )
        value_style = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica',
        )
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#667eea'),
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold',
        )
        note_style = ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#718096'),
            fontName='Helvetica-Oblique',
        )

        story = []

        # Başlık
        story.append(Paragraph(prescription.title, title_style))

        # Tarih ve yazan
        date_str = prescription.created_at.strftime('%d.%m.%Y')
        story.append(Paragraph(
            f'Tarih: {date_str}   |   Yazan: {prescription.created_by.username}',
            subtitle_style,
        ))

        # İşletme bilgisi
        if prescription.farm:
            farm = prescription.farm
            parts = [farm.name]
            loc = ', '.join(filter(None, [farm.mahalle, farm.ilce, farm.il]))
            if loc:
                parts.append(loc)
            if farm.urun_tipi:
                parts.append(farm.urun_tipi.capitalize())
            story.append(Paragraph(f'Isletme: {" | ".join(parts)}', subtitle_style))

        story.append(Spacer(1, 6))
        story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#667eea')))
        story.append(Spacer(1, 6))

        # Açıklama
        if prescription.description:
            story.append(Paragraph('Aciklama', label_style))
            story.append(Paragraph(prescription.description, value_style))
            story.append(Spacer(1, 8))

        # Uygulamalar — session (sulama) yapısı
        sessions = prescription.sessions.prefetch_related('items__product').order_by('sira')

        if sessions.exists():
            for session in sessions:
                tarih_str = session.tarih.strftime('%d.%m.%Y') if session.tarih else ''
                session_title = f'{session.sira}. Sulama'
                if tarih_str:
                    session_title += f'   {tarih_str}'

                story.append(Paragraph(session_title, section_style))

                session_items = session.items.all()
                if session_items.exists():
                    table_data = [['#', 'Ilac / Preparat', 'Dozaj', 'Sera Toplam', 'Uygulama', 'Not']]
                    for item in session_items:
                        urun_adi = item.product.name if item.product else item.urun_adi
                        uygulama = UYGULAMA_TIPI_LABELS.get(item.uygulama_tipi, item.uygulama_tipi)
                        table_data.append([
                            str(item.sira),
                            urun_adi or '-',
                            item.doz or '-',
                            item.sera_toplam or '-',
                            uygulama or '-',
                            item.not_field or '',
                        ])

                    col_widths = [0.7*cm, 4.5*cm, 2.8*cm, 2.8*cm, 3*cm, 3.2*cm]
                    table = Table(table_data, colWidths=col_widths, repeatRows=1)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d8a5e')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
                        ('TOPPADDING', (0, 0), (-1, 0), 7),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TOPPADDING', (0, 1), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                        ('LEFTPADDING', (0, 0), (-1, -1), 5),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0faf5')]),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b2dfdb')),
                        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1a6b47')),
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 8))
                else:
                    story.append(Paragraph('Bu sulama seansinda ilac bulunmuyor.', value_style))
        elif items.exists():
            # Eski format (session olmayan kayıtlar)
            story.append(Paragraph('Uygulama Programi', section_style))
            table_data = [['#', 'Urun / Preparat', 'Doz', 'Uygulama', 'Not']]
            for item in items:
                urun_adi = item.product.name if item.product else item.urun_adi
                uygulama = UYGULAMA_TIPI_LABELS.get(item.uygulama_tipi, item.uygulama_tipi)
                table_data.append([
                    str(item.sira), urun_adi or '-',
                    item.doz or '-', uygulama or '-', item.not_field or '',
                ])
            col_widths = [0.8*cm, 5*cm, 3*cm, 3*cm, 5.2*cm]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f8fc')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#5a67d8')),
            ]))
            story.append(table)
        else:
            story.append(Paragraph('Bu recetede uygulama bulunmuyor.', value_style))

        # Alt bilgi
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f'Bu belge Sera Yonetim Sistemi tarafindan {date_str} tarihinde olusturulmustur.',
            note_style,
        ))

        doc.build(story)
        buffer.seek(0)

        safe_title = prescription.title.replace(' ', '_')[:40]
        filename = f'recete_{prescription.id}_{safe_title}.pdf'

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response
