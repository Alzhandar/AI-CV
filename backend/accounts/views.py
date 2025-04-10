from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializers import UserSerializer, UserProfileSerializer
from rest_framework.decorators import permission_classes, api_view

class RegisterView(generics.CreateAPIView):
    """
    API endpoint для регистрации нового пользователя
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)  # Используйте кортеж вместо списка

class LoginView(APIView):
    """
    API endpoint для входа пользователя
    """
    permission_classes = (AllowAny,)  # Используйте кортеж вместо списка
    
    def post(self, request):
        # ... существующий код ...
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Необходимо указать email и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Неверные учетные данные'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutView(APIView):
    """
    API endpoint для выхода пользователя
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Успешный выход из системы'})

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint для получения и обновления профиля пользователя
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user