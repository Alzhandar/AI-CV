from django.contrib import admin
from resumes.models import Resume, Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'file_type', 'created_at')
    list_filter = ('status', 'file_type', 'created_at')
    search_fields = ('title', 'user__email')
    readonly_fields = ('status', 'mongodb_id', 'created_at', 'updated_at')
    filter_horizontal = ('skills',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)