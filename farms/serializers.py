from rest_framework import serializers
from .models import Farm


class FarmSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Farm
        fields = [
            'id', 'name', 'owner_username',
            'isletme_tipi',
            'il', 'ilce', 'mahalle',
            'sera_tipi', 'buyukluk',
            'urun_tipi', 'urun_cesidi',
            'created_at',
        ]
        read_only_fields = ['id', 'owner_username', 'created_at']
