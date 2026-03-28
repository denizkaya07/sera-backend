from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Token endpoint'leri
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Kullanıcı işlemleri (register, profile)
    path('api/users/', include('users.urls')),

    # Reçete işlemleri
    path('api/', include('prescriptions.urls')),
]
