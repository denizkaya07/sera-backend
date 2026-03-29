from rest_framework import serializers
from .models import Prescription, PrescriptionItem


class PrescriptionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = PrescriptionItem
        fields = ['id', 'sira', 'uygulama_tipi', 'product', 'product_name', 'urun_adi', 'doz', 'not_field']


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, required=False)
    farm_name = serializers.ReadOnlyField(source='farm.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Prescription
        fields = ['id', 'title', 'description', 'farm', 'farm_name', 'created_by_username', 'items', 'created_at']
        read_only_fields = ['id', 'farm_name', 'created_by_username', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        prescription = Prescription.objects.create(**validated_data)
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
        return prescription
