from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Prescription
from .serializers import PrescriptionSerializer
from invitations.models import FarmPermission
from django.utils import timezone


class PrescriptionViewSet(ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        farm_id = self.request.query_params.get('farm_id')

        if user.role == 'farmer':
            qs = Prescription.objects.filter(farm__owner=user)
        else:
            permitted_farm_ids = FarmPermission.objects.filter(
                invitation__sender=user,
                is_active=True,
                year=timezone.now().year
            ).values_list('farm_id', flat=True)
            qs = Prescription.objects.filter(farm_id__in=permitted_farm_ids)

        if farm_id:
            qs = qs.filter(farm_id=farm_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
