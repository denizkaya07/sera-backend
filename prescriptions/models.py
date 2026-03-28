from django.db import models
from django.conf import settings
from django.utils import timezone


class Prescription(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title