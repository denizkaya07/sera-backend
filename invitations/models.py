from django.db import models
from django.conf import settings
from django.utils import timezone


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_invitations'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"


class FarmPermission(models.Model):
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name='permissions')
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='permissions')
    year = models.IntegerField(default=timezone.now().year)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('invitation', 'farm', 'year')

    def __str__(self):
        return f"{self.invitation} - {self.farm.name} ({self.year})"


class FarmNote(models.Model):
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.farm.name} - {self.author.username}"
