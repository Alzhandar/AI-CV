from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from resumes.models import Skill, Resume


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'related_resumes_count', 'related_jobs_count')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def related_resumes_count(self, obj):
        count = obj.resumes.count()
        if count == 0:
            return "0"
        
        url = reverse('admin:resumes_resume_changelist') + f'?skills__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    related_resumes_count.short_description = _('Резюме')
    
    def related_jobs_count(self, obj):
        try:
            count = obj.jobs.count()
            if count == 0:
                return "0"
                
            url = reverse('admin:jobs_job_changelist') + f'?required_skills__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        except:
            return "-"
    related_jobs_count.short_description = _('Вакансии')
    
    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if obj.resumes.exists():
                return False
            try:
                if obj.jobs.exists():
                    return False
            except:
                pass
        return super().has_delete_permission(request, obj)


class SkillInline(admin.TabularInline):
    model = Resume.skills.through
    verbose_name = _("Навык")
    verbose_name_plural = _("Навыки")
    extra = 1
    autocomplete_fields = ['skill']


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'file_preview', 'status', 'skills_count', 'created_at')
    list_filter = ('status', 'file_type', 'created_at')
    search_fields = ('title', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'mongodb_id', 'file_preview')
    raw_id_fields = ('user',)
    inlines = [SkillInline]
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'user', 'file', 'file_type', 'file_preview')
        }),
        (_('Статус анализа'), {
            'fields': ('status', 'mongodb_id'),
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_preview(self, obj):
        if obj.file:
            file_name = obj.get_file_name()
            file_url = obj.file.url
            return format_html('<a href="{}" target="_blank">{}</a>', file_url, file_name)
        return "-"
    file_preview.short_description = _('Просмотр файла')
    
    def skills_count(self, obj):
        count = obj.skills.count()
        if count == 0:
            return "0"
        
        skills_list = ", ".join([skill.name for skill in obj.skills.all()[:5]])
        if obj.skills.count() > 5:
            skills_list += "..."
            
        return format_html('<span title="{}">{}</span>', skills_list, count)
    skills_count.short_description = _('Навыки')
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('skills')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if not change or 'file' in form.changed_data:
            try:
                from resumes.tasks import analyze_resume
                analyze_resume.delay(obj.id)
            except Exception as e:
                self.message_user(request, 
                                 f"Произошла ошибка при запуске анализа: {str(e)}", 
                                 level='ERROR')