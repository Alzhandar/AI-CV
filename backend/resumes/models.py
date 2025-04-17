from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from typing import List, Set, Dict, Any, Optional


class Skill(models.Model):
    PROGRAMMING = 'programming'
    FRAMEWORK = 'framework'
    DATABASE = 'database'
    DEVOPS = 'devops'
    SOFT_SKILL = 'soft_skill'
    LANGUAGE = 'language'
    OTHER = 'other'
    
    CATEGORY_CHOICES = (
        (PROGRAMMING, _('Языки программирования')),
        (FRAMEWORK, _('Фреймворки и библиотеки')),
        (DATABASE, _('Базы данных')),
        (DEVOPS, _('DevOps и инфраструктура')),
        (SOFT_SKILL, _('Гибкие навыки')),
        (LANGUAGE, _('Языки')),
        (OTHER, _('Другое')),
    )
    
    name = models.CharField(_('название'), max_length=100, unique=True)
    category = models.CharField(
        _('категория'),
        max_length=50, 
        choices=CATEGORY_CHOICES,
        default=OTHER
    )
    slug = models.SlugField(_('URL-идентификатор'), max_length=110, unique=True, blank=True)
    description = models.TextField(_('описание'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата изменения'), auto_now=True)
    
    class Meta:
        verbose_name = _('навык')
        verbose_name_plural = _('навыки')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            count = 1
            while Skill.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)


class Resume(models.Model):
    PENDING = 'pending'
    ANALYZING = 'analyzing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = (
        (PENDING, _('В ожидании')),
        (ANALYZING, _('Анализируется')),
        (COMPLETED, _('Анализ завершен')),
        (FAILED, _('Ошибка анализа')),
    )
    
    PDF = 'pdf'
    DOCX = 'docx'
    
    FILE_TYPE_CHOICES = (
        (PDF, _('PDF')),
        (DOCX, _('Microsoft Word')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='resumes',
        verbose_name=_('пользователь')
    )
    title = models.CharField(_('название'), max_length=255)
    file = models.FileField(_('файл'), upload_to='resumes/')
    file_type = models.CharField(
        _('тип файла'), 
        max_length=10, 
        choices=FILE_TYPE_CHOICES
    )
    
    status = models.CharField(
        _('статус'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=PENDING
    )
    
    mongodb_id = models.CharField(
        _('ID в MongoDB'), 
        max_length=24, 
        blank=True, 
        null=True
    )
    
    skills = models.ManyToManyField(
        Skill, 
        blank=True,
        related_name='resumes',
        verbose_name=_('навыки')
    )
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата изменения'), auto_now=True)
    
    class Meta:
        verbose_name = _('резюме')
        verbose_name_plural = _('резюме')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.title} - {self.user.email}"
    
    def clean(self) -> None:
        if self.file:
            file_ext = self.file.name.split('.')[-1].lower()
            if self.file_type == self.PDF and file_ext != 'pdf':
                raise ValidationError({
                    'file': _("Тип файла не совпадает с выбранным типом. Ожидается PDF.")
                })
            elif self.file_type == self.DOCX and file_ext != 'docx':
                raise ValidationError({
                    'file': _("Тип файла не совпадает с выбранным типом. Ожидается DOCX.")
                })
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.file and not self.file_type:
            file_ext = self.file.name.split('.')[-1].lower()
            if file_ext == 'pdf':
                self.file_type = self.PDF
            elif file_ext == 'docx':
                self.file_type = self.DOCX
        super().save(*args, **kwargs)
    
    def get_skills_list(self) -> List[str]:
        return list(self.skills.values_list('name', flat=True))
    
    def get_file_name(self) -> str:
        return self.file.name.split('/')[-1] if self.file else ""
    
    @property
    def is_analyzed(self) -> bool:
        return self.status == self.COMPLETED