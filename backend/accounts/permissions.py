from rest_framework import permissions
from typing import Any, Optional

from accounts.models import User


class IsJobseeker(permissions.BasePermission):
    message = 'Доступ разрешен только соискателям.'
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.JOBSEEKER


class IsEmployer(permissions.BasePermission):
    message = 'Доступ разрешен только работодателям.'
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.EMPLOYER


class IsAdmin(permissions.BasePermission):
    message = 'Доступ разрешен только администраторам.'
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.ADMIN


class IsOwnerOrAdmin(permissions.BasePermission):
    message = 'Доступ разрешен только владельцу ресурса или администратору.'
    
    def has_object_permission(self, request, view, obj: Any) -> bool:
        if request.user.role == User.ADMIN:
            return True
            
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        if hasattr(obj, 'company') and hasattr(obj.company, 'user'):
            return obj.company.user == request.user
            
        if isinstance(obj, User):
            return obj == request.user
            
        return False


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS