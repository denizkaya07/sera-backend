from django.db import models
from django.conf import settings
from django.utils import timezone


class Product(models.Model):
    URUN_TIPI = [
        ('ilac', 'Ilac'),
        ('gubre', 'Gubre'),
        ('diger', 'Diger'),
    ]

    EKLEYEN_RENK = {
        'dealer': '#3182ce',     # mavi - bayi
        'engineer': '#38a169',   # yesil - muhendis
        'producer': '#dd6b20',   # turuncu - uretici firma
    }

    name = models.CharField(max_length=255)
    urun_tipi = models.CharField(max_length=20, choices=URUN_TIPI, default='ilac')
    etken_madde = models.CharField(max_length=255, blank=True, default='')
    doz = models.CharField(max_length=100, blank=True, default='')
    kullanim_amaci = models.TextField(blank=True, default='')
    uretici = models.CharField(max_length=255, blank=True, default='')
    ozellikler = models.TextField(blank=True, default='')

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_products'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def renk(self):
        if self.added_by:
            return self.EKLEYEN_RENK.get(self.added_by.role, '#718096')
        return '#718096'


class BkuUrun(models.Model):
        bitki = models.CharField(max_length=255)
        aktif_madde = models.CharField(max_length=255, blank=True, default='')
        ruhsat_no = models.CharField(max_length=100, blank=True, default='')
        urun_adi = models.CharField(max_length=255)
        etken_madde = models.CharField(max_length=255, blank=True, default='')
        firma = models.CharField(max_length=255, blank=True, default='')
        doz = models.CharField(max_length=255, blank=True, default='')
        zarali = models.CharField(max_length=255, blank=True, default='')
        son_ilac_hasat = models.CharField(max_length=100, blank=True, default='')
        created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
                ordering = ['bitki', 'urun_adi']
                unique_together = ('ruhsat_no', 'bitki', 'zarali')

    def __str__(self):
                return f"{self.urun_adi} - {self.bitki}"
