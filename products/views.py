from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all()
        urun_tipi = self.request.query_params.get('urun_tipi')
        if urun_tipi:
            qs = qs.filter(urun_tipi=urun_tipi)
        return qs

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        if product.added_by != request.user and not request.user.is_superuser:
            return Response({'error': 'Sadece kendi eklediginiz urunleri duzenleyebilirsiniz.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product.added_by != request.user and not request.user.is_superuser:
            return Response({'error': 'Sadece kendi eklediginiz urunleri silebilirsiniz.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
