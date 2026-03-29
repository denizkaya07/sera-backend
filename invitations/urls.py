from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvitationViewSet, FarmPermissionViewSet, FarmNoteViewSet

router = DefaultRouter()
router.register(r'invitations', InvitationViewSet, basename='invitation')
router.register(r'farm-permissions', FarmPermissionViewSet, basename='farmpermission')
router.register(r'farm-notes', FarmNoteViewSet, basename='farmnote')

urlpatterns = [
    path('', include(router.urls)),
]
