from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from typing import Optional, Any, Dict, Union


class UserManager(BaseUserManager):
    
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Dict[str, Any]) -> 'User':
        if not email:
            raise ValueError(_('Email обязателен для регистрации'))
            
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields: Dict[str, Any]) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    JOBSEEKER = 'jobseeker'
    EMPLOYER = 'employer'
    ADMIN = 'admin'
    
    ROLE_CHOICES = (
        (JOBSEEKER, _('Соискатель')),
        (EMPLOYER, _('Работодатель')),
        (ADMIN, _('Администратор')),
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Номер телефона должен быть в формате: '+999999999'. До 15 цифр разрешено.")
    )
    
    username = None  
    email = models.EmailField(_('email адрес'), unique=True, db_index=True)
    role = models.CharField(_('роль'), max_length=20, choices=ROLE_CHOICES, default=JOBSEEKER)
    
    phone = models.CharField(_('телефон'), max_length=20, validators=[phone_regex], blank=True, null=True)
    bio = models.TextField(_('о себе'), blank=True, null=True)
    profile_picture = models.ImageField(_('фото профиля'), upload_to='profile_pics/', blank=True, null=True)
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.email
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    @property
    def is_jobseeker(self) -> bool:
        """Проверка, является ли пользователь соискателем"""
        return self.role == self.JOBSEEKER
    
    @property
    def is_employer(self) -> bool:
        """Проверка, является ли пользователь работодателем"""
        return self.role == self.EMPLOYER
    
    @property
    def is_admin_user(self) -> bool:
        """Проверка, является ли пользователь администратором"""
        return self.role == self.ADMIN