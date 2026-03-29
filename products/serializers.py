from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    added_by_username = serializers.ReadOnlyField(source='added_by.username')
    added_by_role = serializers.ReadOnlyField(source='added_by.role')
    renk = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'urun_tipi', 'etken_madde', 'doz', 'kullanim_amaci', 'uretici', 'ozellikler', 'added_by_username', 'added_by_role', 'renk', 'created_at']
        read_only_fields = ['id', 'added_by_username', 'added_by_role', 'renk', 'created_at']
