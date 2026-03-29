from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'urun_tipi', 'added_by', 'created_at')
    list_filter = ('urun_tipi',)
    search_fields = ('name', 'etken_madde')