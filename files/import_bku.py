"""
BKU JSON -> Django DB import management command
Kullanim:
    python manage.py import_bku                          # bku_domates_sera.json (varsayilan)
    python manage.py import_bku --file bku_domates_sera.json
    python manage.py import_bku --file tum_bitkiler.json --clear
"""

import json
import os
from django.core.management.base import BaseCommand
from products.models import BkuUrun


class Command(BaseCommand):
    help = "BKU scraper JSON çıktısını veritabanına aktarır"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='bku_domates_sera.json',
            help='JSON dosyasının adı (varsayılan: bku_domates_sera.json)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Import öncesi tüm BkuUrun kayıtlarını sil',
        )

    def handle(self, *args, **options):
        dosya = options['file']

        # Dosyayı manage.py ile aynı klasörde ara
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )))
        dosya_yolu = os.path.join(base_dir, dosya)

        if not os.path.exists(dosya_yolu):
            self.stderr.write(self.style.ERROR(f"Dosya bulunamadı: {dosya_yolu}"))
            return

        # --clear seçeneği
        if options['clear']:
            sayi = BkuUrun.objects.all().count()
            BkuUrun.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"{sayi} kayıt silindi."))

        # JSON oku
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            urunler = json.load(f)

        self.stdout.write(f"{len(urunler)} ürün okundu: {dosya}")

        eklenen = 0
        atlanan = 0

        for u in urunler:
            try:
                obj, created = BkuUrun.objects.get_or_create(
                    ruhsat_no  = u.get('ruhsat_no', ''),
                    bitki      = u.get('bitki', ''),
                    zarali     = u.get('zarali', ''),
                    defaults={
                        'aktif_madde'    : u.get('aktif_madde', ''),
                        'urun_adi'       : u.get('urun_adi', ''),
                        'etken_madde'    : u.get('etken_madde', ''),
                        'firma'          : u.get('firma', ''),
                        'doz'            : u.get('doz', ''),
                        'son_ilac_hasat' : u.get('son_ilac_hasat', ''),
                    }
                )
                if created:
                    eklenen += 1
                else:
                    atlanan += 1

            except Exception as e:
                self.stderr.write(f"HATA: {e} | Ürün: {u.get('urun_adi', '?')}")

        self.stdout.write(self.style.SUCCESS(
            f"\nTamamlandı: {eklenen} eklendi, {atlanan} zaten vardı."
        ))
