from django.db import models
from django.conf import settings


class Farm(models.Model):

    ISLETME_TIPI = [
        ('sera', 'Sera'),
        ('bahce', 'Bahce'),
        ('tarla', 'Tarla'),
        ('fidelik', 'Fidelik'),
        ('diger', 'Diger'),
    ]

    SERA_TIPI = [
        ('cam', 'Cam Sera'),
        ('plastik', 'Plastik Sera'),
        ('polykarbon', 'Polykarbon Sera'),
        ('diger', 'Diger'),
    ]

    URUN_TIPI = [
        ('domates', 'Domates'),
        ('biber', 'Biber'),
        ('salatalik', 'Salatalik'),
        ('patlican', 'Patlican'),
        ('marul', 'Marul'),
        ('diger', 'Diger'),
    ]

    # Temel bilgiler
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    isletme_tipi = models.CharField(max_length=20, choices=ISLETME_TIPI, blank=True, default='sera')

    # Cografi konum
    il = models.CharField(max_length=100, blank=True, default='')
    ilce = models.CharField(max_length=100, blank=True, default='')
    mahalle = models.CharField(max_length=100, blank=True, default='')

    # Sera bilgileri (sadece sera tipinde)
    sera_tipi = models.CharField(max_length=20, choices=SERA_TIPI, blank=True, default='')
    buyukluk = models.FloatField(null=True, blank=True, help_text='Metrekare')

    # Urun bilgileri
    urun_tipi = models.CharField(max_length=20, choices=URUN_TIPI, blank=True, default='')
    urun_cesidi = models.CharField(max_length=100, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
