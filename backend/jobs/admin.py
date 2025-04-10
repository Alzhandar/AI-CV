from django.contrib import admin
from jobs.models import Company, Job

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'website', 'created_at')
    search_fields = ('name', 'user__email')
    list_filter = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'status', 'location', 'created_at')
    list_filter = ('status', 'created_at', 'company')
    search_fields = ('title', 'company__name', 'location')
    filter_horizontal = ('required_skills',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company__user=request.user)