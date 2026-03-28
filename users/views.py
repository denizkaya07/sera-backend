from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json

User = get_user_model()


def home(request):
    return JsonResponse({"message": "API çalışıyor 🚀"})


@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Sadece POST metodu kabul edilir.'}, status=405)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON.'}, status=400)

    username = body.get('username', '').strip()
    password = body.get('password', '').strip()

    if not username or not password:
        return JsonResponse({'error': 'Kullanıcı adı ve şifre zorunludur.'}, status=400)
    if len(password) < 6:
        return JsonResponse({'error': 'Şifre en az 6 karakter olmalıdır.'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Bu kullanıcı adı zaten alınmış.'}, status=400)

    User.objects.create_user(username=username, password=password)
    return JsonResponse({'message': 'Kayıt başarılı.'}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        'user': request.user.username,
        'role': request.user.role,
        'email': request.user.email,
    })