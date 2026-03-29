from rest_framework import serializers
from .models import Invitation, FarmPermission, FarmNote


class InvitationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    sender_role = serializers.ReadOnlyField(source='sender.role')
    receiver_username = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = Invitation
        fields = ['id', 'sender', 'sender_username', 'sender_role', 'receiver', 'receiver_username', 'status', 'message', 'created_at']
        read_only_fields = ['id', 'sender', 'sender_username', 'sender_role', 'receiver_username', 'status', 'created_at']


class FarmPermissionSerializer(serializers.ModelSerializer):
    farm_name = serializers.ReadOnlyField(source='farm.name')
    farmer_username = serializers.ReadOnlyField(source='farm.owner.username')

    class Meta:
        model = FarmPermission
        fields = ['id', 'farm', 'farm_name', 'farmer_username', 'year', 'is_active']


class FarmNoteSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    author_role = serializers.ReadOnlyField(source='author.role')

    class Meta:
        model = FarmNote
        fields = ['id', 'farm', 'author_username', 'author_role', 'content', 'created_at']
        read_only_fields = ['id', 'author_username', 'author_role', 'created_at']
