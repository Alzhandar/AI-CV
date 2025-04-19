from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.db import transaction

from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.authtoken.models import Token

from .models import User
from .serializers import UserSerializer, UserProfileSerializer, PasswordChangeSerializer
from .permissions import IsOwnerOrAdmin

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]
    
    @method_decorator(sensitive_post_parameters('password', 'password_confirm'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print(f"Registration request data: {request.data}")  # Логирование запроса
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")  # Логирование ошибок
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = self.perform_create(serializer)
        token, _ = Token.objects.get_or_create(user=user)
        
        login(request, user)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'token': token.key,
            'user': serializer.data,
            'message': f'Аккаунт успешно создан. Добро пожаловать, {user.full_name}!'
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        return serializer.save()

class LoginView(views.APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]
    
    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Необходимо указать email и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if not user.is_active:
                return Response(
                    {'error': 'Аккаунт деактивирован'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            login(request, user)
            
            # Получаем или создаем токен для пользователя
            token, _ = Token.objects.get_or_create(user=user)
            
            serializer = UserSerializer(user)
            return Response({
                'token': token.key,  
                'user': serializer.data,
                'message': f'Добро пожаловать, {user.full_name}!'
            })
        else:
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Удаляем токен при выходе
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
            
        # Стандартный выход из системы
        logout(request)
        
        return Response({
            'message': 'Успешный выход из системы'
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [UserRateThrottle]
    
    @method_decorator(sensitive_post_parameters())
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Всегда используем частичное обновление
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
            
        return Response(serializer.data)


class PasswordChangeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    throttle_classes = [UserRateThrottle]

    @method_decorator(sensitive_post_parameters('current_password', 'new_password', 'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Изменяем пароль
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Обновляем токен для дополнительной безопасности
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)
        
        # Повторная авторизация с новым токеном
        login(request, user)
        
        return Response({
            'message': 'Пароль успешно изменен',
            'token': token.key
        }, status=status.HTTP_200_OK)