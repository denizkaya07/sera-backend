from django.contrib import admin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'created_at')