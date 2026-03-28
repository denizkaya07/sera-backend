from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('engineer', 'Mühendis'),
        ('farmer', 'Çiftçi'),
        ('dealer', 'Bayii'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)