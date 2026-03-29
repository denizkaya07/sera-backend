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
