from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import User
from .serializers import UserSerializer, UserProfileSerializer
from .permissions import IsOwnerOrAdmin


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]
    
    @method_decorator(sensitive_post_parameters('password', 'password_confirm'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        
        login(request, user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
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
            
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)
            
            serializer = UserSerializer(user)
            user_data = serializer.data
            
            return Response({
                'token': token.key,  
                'user': user_data,
                'message': f'Добро пожаловать, {user.full_name}!'
            })
        else:
            return Response(
                {'error': 'Неверные учетные данные'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Успешный выход из системы'
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [UserRateThrottle]
    
    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self):

        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
            
        return Response(serializer.data)