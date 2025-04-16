from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User
from typing import Dict, Any


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone', 
            'bio', 'profile_picture', 'created_at', 'full_name'
        ]
        read_only_fields = ['id', 'created_at', 'full_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate_email(self, value: str) -> str:
        user = User.objects.filter(email=value.lower())
        if self.instance:
            user = user.exclude(pk=self.instance.pk)
        if user.exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value.lower()
    
    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': ["Пароли не совпадают."]})
        
        attrs.pop('password_confirm', None)
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('password_confirm', None)
        
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
    
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('password_confirm', None)
        
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'role', 'phone', 'bio', 'profile_picture',
            'full_name', 'is_jobseeker', 'is_employer', 'is_admin_user'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_jobseeker', 'is_employer', 'is_admin_user']