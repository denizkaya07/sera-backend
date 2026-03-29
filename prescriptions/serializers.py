from rest_framework import serializers
from .models import Prescription, PrescriptionSession, PrescriptionItem


class PrescriptionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'sira', 'uygulama_tipi',
            'product', 'product_name',
            'urun_adi', 'doz', 'sera_toplam', 'not_field',
        ]


class PrescriptionSessionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, required=False)

    class Meta:
        model = PrescriptionSession
        fields = ['id', 'sira', 'tarih', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        session = PrescriptionSession.objects.create(**validated_data)
        for idx, item_data in enumerate(items_data, 1):
            item_data.setdefault('sira', idx)
            PrescriptionItem.objects.create(session=session, **item_data)
        return session


class PrescriptionSerializer(serializers.ModelSerializer):
    sessions = PrescriptionSessionSerializer(many=True, required=False)
    items = PrescriptionItemSerializer(many=True, required=False)
    farm_name = serializers.ReadOnlyField(source='farm.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Prescription
        fields = [
            'id', 'title', 'description',
            'farm', 'farm_name',
            'created_by_username',
            'sessions', 'items',
            'created_at',
        ]
        read_only_fields = ['id', 'farm_name', 'created_by_username', 'created_at']

    def create(self, validated_data):
        sessions_data = validated_data.pop('sessions', [])
        items_data = validated_data.pop('items', [])
        prescription = Prescription.objects.create(**validated_data)

        for s_idx, session_data in enumerate(sessions_data, 1):
            items = session_data.pop('items', [])
            session_data.setdefault('sira', s_idx)
            session = PrescriptionSession.objects.create(
                prescription=prescription, **session_data
            )
            for i_idx, item_data in enumerate(items, 1):
                item_data.setdefault('sira', i_idx)
                PrescriptionItem.objects.create(session=session, **item_data)

        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)

        return prescription
