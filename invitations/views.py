from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Invitation, FarmPermission, FarmNote
from .serializers import InvitationSerializer, FarmPermissionSerializer, FarmNoteSerializer

User = get_user_model()


class InvitationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InvitationSerializer

    def get_queryset(self):
        user = self.request.user
        return Invitation.objects.filter(
            sender=user
        ) | Invitation.objects.filter(receiver=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def received(self, request):
        invitations = Invitation.objects.filter(receiver=request.user, status='pending')
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        invitation = self.get_object()
        if invitation.receiver != request.user:
            return Response({'error': 'Yetkiniz yok.'}, status=status.HTTP_403_FORBIDDEN)
        if invitation.status != 'pending':
            return Response({'error': 'Bu davet zaten yanıtlanmış.'}, status=status.HTTP_400_BAD_REQUEST)

        farm_ids = request.data.get('farm_ids', [])
        if not farm_ids:
            return Response({'error': 'En az bir sera seçmelisiniz.'}, status=status.HTTP_400_BAD_REQUEST)

        invitation.status = 'accepted'
        invitation.save()

        year = timezone.now().year
        for farm_id in farm_ids:
            FarmPermission.objects.get_or_create(
                invitation=invitation,
                farm_id=farm_id,
                year=year,
                defaults={'is_active': True}
            )

        return Response({'message': 'Davet kabul edildi.'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        invitation = self.get_object()
        if invitation.receiver != request.user:
            return Response({'error': 'Yetkiniz yok.'}, status=status.HTTP_403_FORBIDDEN)
        invitation.status = 'rejected'
        invitation.save()
        return Response({'message': 'Davet reddedildi.'})

    @action(detail=False, methods=['get'])
    def search_farmer(self, request):
        username = request.query_params.get('username', '')
        if not username:
            return Response({'error': 'Kullanici adi gerekli.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            farmer = User.objects.get(username=username, role='farmer')
            return Response({'id': farmer.id, 'username': farmer.username, 'role': farmer.role})
        except User.DoesNotExist:
            return Response({'error': 'Ciftci bulunamadi.'}, status=status.HTTP_404_NOT_FOUND)


class FarmPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FarmPermissionSerializer

    def get_queryset(self):
        user = self.request.user
        return FarmPermission.objects.filter(
            invitation__sender=user,
            is_active=True,
            year=timezone.now().year
        )

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        permission = self.get_object()
        if permission.invitation.sender != request.user:
            return Response({'error': 'Yetkiniz yok.'}, status=status.HTTP_403_FORBIDDEN)
        new_year = timezone.now().year
        new_perm, created = FarmPermission.objects.get_or_create(
            invitation=permission.invitation,
            farm=permission.farm,
            year=new_year,
            defaults={'is_active': True}
        )
        if not created:
            return Response({'error': 'Bu yil icin izin zaten var.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f'{new_year} yili icin izin yenilendi.'})


class FarmNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FarmNoteSerializer

    def get_queryset(self):
        user = self.request.user
        farm_id = self.request.query_params.get('farm_id')

        permitted_farm_ids = FarmPermission.objects.filter(
            invitation__sender=user,
            is_active=True,
            year=timezone.now().year
        ).values_list('farm_id', flat=True)

        qs = FarmNote.objects.filter(farm_id__in=permitted_farm_ids)
        if farm_id:
            qs = qs.filter(farm_id=farm_id)
        return qs

    def perform_create(self, serializer):
        farm = serializer.validated_data['farm']
        user = self.request.user
        has_permission = FarmPermission.objects.filter(
            invitation__sender=user,
            farm=farm,
            is_active=True,
            year=timezone.now().year
        ).exists()
        if not has_permission:
            raise PermissionError('Bu seraya erisim izniniz yok.')
        serializer.save(author=user)
