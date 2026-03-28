from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


@api_view(['GET'])
def home(request):
    return Response({"message": "API çalışıyor 🚀"})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    role = request.data.get('role', '').strip()

    if not username or not password:
        return Response({'error': 'Kullanıcı adı ve şifre zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({'error': 'Şifre en az 6 karakter olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Bu kullanıcı adı zaten alınmış.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    if role in ['engineer', 'farmer', 'dealer']:
        user.role = role
        user.save()

    return Response({'message': 'Kayıt başarılı.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        'user': request.user.username,
        'role': request.user.role,
        'email': request.user.email,
    })