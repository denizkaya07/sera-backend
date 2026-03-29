from django.db import models
from django.conf import settings
from django.utils import timezone


class Prescription(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='prescriptions',
        null=True, blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class PrescriptionSession(models.Model):
    """Her sulama seansını temsil eder (1. Sulama, 2. Sulama ...)"""
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    sira = models.PositiveIntegerField(default=1)
    tarih = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['sira']

    def __str__(self):
        tarih_str = self.tarih.strftime('%d.%m.%Y') if self.tarih else ''
        return f"{self.prescription.title} - {self.sira}. Sulama {tarih_str}"


class PrescriptionItem(models.Model):
    UYGULAMA_TIPI = [
        ('yapraktan', 'Yapraktan'),
        ('topraktan', 'Topraktan'),
        ('sulamayla', 'Sulamayla'),
        ('damla_sulama', 'Damla Sulama'),
        ('yagmurlama', 'Yagmurlama'),
    ]

    # Eski kayıtlar için prescription FK korundu (nullable)
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items',
        null=True, blank=True
    )
    # Yeni format: session üzerinden bağlı
    session = models.ForeignKey(
        PrescriptionSession,
        on_delete=models.CASCADE,
        related_name='items',
        null=True, blank=True
    )
    sira = models.PositiveIntegerField(default=1)
    uygulama_tipi = models.CharField(max_length=20, choices=UYGULAMA_TIPI, blank=True, default='')
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prescription_items'
    )
    urun_adi = models.CharField(max_length=255, blank=True, default='')
    doz = models.CharField(max_length=100, blank=True, default='')
    sera_toplam = models.CharField(max_length=100, blank=True, default='')
    not_field = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['sira']

    def __str__(self):
        parent = self.session or self.prescription
        return f"{parent} - {self.sira}. uygulama"
