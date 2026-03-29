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


class PrescriptionItem(models.Model):
    UYGULAMA_TIPI = [
        ('yapraktan', 'Yapraktan'),
        ('topraktan', 'Topraktan'),
        ('sulamayla', 'Sulamayla'),
    ]

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    sira = models.PositiveIntegerField(default=1)
    uygulama_tipi = models.CharField(max_length=20, choices=UYGULAMA_TIPI, default='sulamayla')
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prescription_items'
    )
    urun_adi = models.CharField(max_length=255, blank=True, default='')
    doz = models.CharField(max_length=100, blank=True, default='')
    not_field = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['sira']

    def __str__(self):
        return f"{self.prescription.title} - {self.sira}. uygulama"
