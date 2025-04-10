from django.db import models
from django.conf import settings
from resumes.models import Skill

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        return self.name

class Job(models.Model):
    ACTIVE = 'active'
    CLOSED = 'closed'
    DRAFT = 'draft'
    
    STATUS_CHOICES = (
        (ACTIVE, 'Активная'),
        (CLOSED, 'Закрыта'),
        (DRAFT, 'Черновик'),
    )
    
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    requirements = models.TextField()
    
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    location = models.CharField(max_length=255, blank=True, null=True)
    
    required_skills = models.ManyToManyField(Skill, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} в {self.company.name}"