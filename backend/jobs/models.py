from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from resumes.models import Skill
from typing import Optional, List, Set


class Company(models.Model):
    name = models.CharField(_('название'), max_length=255, db_index=True)
    slug = models.SlugField(_('URL-идентификатор'), max_length=255, unique=True, blank=True)
    description = models.TextField(_('описание'), blank=True, null=True)
    website = models.URLField(_('веб-сайт'), blank=True, null=True, validators=[URLValidator()])
    logo = models.ImageField(_('логотип'), upload_to='company_logos/', blank=True, null=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name=_('пользователь'),
        related_name='companies'
    )
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('компания')
        verbose_name_plural = _('компании')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
            original_slug = self.slug
            count = 1
            while Company.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
                
        super().save(*args, **kwargs)
    
    @property
    def active_jobs_count(self) -> int:
        return self.jobs.filter(status=Job.ACTIVE).count()
    
    def get_absolute_url(self) -> str:
        return f"/companies/{self.slug}/"


class Job(models.Model):
    ACTIVE = 'active'
    CLOSED = 'closed'
    DRAFT = 'draft'
    
    STATUS_CHOICES = (
        (ACTIVE, _('Активная')),
        (CLOSED, _('Закрыта')),
        (DRAFT, _('Черновик')),
    )
    
    title = models.CharField(_('название'), max_length=255, db_index=True)
    slug = models.SlugField(_('URL-идентификатор'), max_length=255, blank=True)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='jobs',
        verbose_name=_('компания')
    )
    description = models.TextField(_('описание'))
    requirements = models.TextField(_('требования'))
    
    salary_min = models.DecimalField(
        _('минимальная зарплата'),
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    salary_max = models.DecimalField(
        _('максимальная зарплата'),
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    location = models.CharField(_('местоположение'), max_length=255, blank=True, null=True)
    
    required_skills = models.ManyToManyField(
        Skill, 
        blank=True,
        related_name='jobs',
        verbose_name=_('требуемые навыки')
    )
    
    status = models.CharField(
        _('статус'),
        max_length=10, 
        choices=STATUS_CHOICES, 
        default=DRAFT,
        db_index=True
    )
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('вакансия')
        verbose_name_plural = _('вакансии')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['status']),
            models.Index(fields=['location']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.title} в {self.company.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{self.company.slug}"
            
            original_slug = self.slug
            count = 1
            while Job.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
                
        if self.salary_min and self.salary_max and self.salary_min > self.salary_max:
            self.salary_min, self.salary_max = self.salary_max, self.salary_min
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self) -> str:
        return f"/jobs/{self.slug}/"
    
    @property
    def salary_display(self) -> str:
        if self.salary_min and self.salary_max:
            if self.salary_min == self.salary_max:
                return f"{int(self.salary_min):,}".replace(',', ' ')
            return f"от {int(self.salary_min):,} до {int(self.salary_max):,}".replace(',', ' ')
        elif self.salary_min:
            return f"от {int(self.salary_min):,}".replace(',', ' ')
        elif self.salary_max:
            return f"до {int(self.salary_max):,}".replace(',', ' ')
        return "Договорная"
    
    def get_required_skills_list(self) -> List[str]:
        return list(self.required_skills.values_list('name', flat=True))