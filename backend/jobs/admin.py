from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count

from jobs.models import Company, Job


class JobInline(admin.TabularInline):
    model = Job
    extra = 0
    show_change_link = True
    fields = ('title', 'status', 'location', 'created_at')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
            
        if obj and obj.user == request.user:
            return True
            
        return False


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'website', 'active_jobs_count', 'logo_preview', 'created_at')
    search_fields = ('name', 'user__email', 'description')
    list_filter = ('created_at', 'user')
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [JobInline]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'user', 'description')
        }),
        (_('Контактная информация'), {
            'fields': ('website', 'logo', 'logo_preview')
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" height="auto" />', obj.logo.url)
        return "-"
    logo_preview.short_description = _('Логотип (превью)')
    
    def active_jobs_count(self, obj):
        return obj.jobs.filter(status=Job.ACTIVE).count()
    active_jobs_count.short_description = _('Активные вакансии')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).annotate(
            jobs_count=Count('jobs')
        )
        
        if request.user.is_superuser:
            return qs
            
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.user == request.user
        
    def has_delete_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.user == request.user


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'status', 'location', 'salary_display', 'created_at')
    list_filter = ('status', 'created_at', 'company')
    search_fields = ('title', 'company__name', 'location', 'description')
    filter_horizontal = ('required_skills',)
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'slug', 'company', 'status', 'description', 'requirements')
        }),
        (_('Требования и условия'), {
            'fields': ('salary_min', 'salary_max', 'location', 'required_skills')
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('company')
        
        if request.user.is_superuser:
            return qs
            
        return qs.filter(company__user=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company" and not request.user.is_superuser:
            kwargs["queryset"] = Company.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.company.user == request.user
        
    def has_delete_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.company.user == request.user