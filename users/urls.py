from django.urls import path
from .views import home, register, profile

urlpatterns = [
    path('', home),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
]
