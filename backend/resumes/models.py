from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Resume(models.Model):
    PENDING = 'pending'
    ANALYZING = 'analyzing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = (
        (PENDING, 'В ожидании'),
        (ANALYZING, 'Анализируется'),
        (COMPLETED, 'Анализ завершен'),
        (FAILED, 'Ошибка анализа'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resumes/')
    file_type = models.CharField(max_length=10)  # pdf, docx, etc.
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    mongodb_id = models.CharField(max_length=24, blank=True, null=True)
    
    skills = models.ManyToManyField(Skill, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"