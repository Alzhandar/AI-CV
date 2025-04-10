from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import RegisterView, LoginView, LogoutView, UserProfileView
from resumes.views import ResumeViewSet, SkillViewSet, AnalysisHistoryViewSet
from jobs.views import CompanyViewSet, JobViewSet
from django.contrib import admin

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'history', AnalysisHistoryViewSet, basename='history')  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), 
    path('api/', include('accounts.urls')), 
    path('api/', include('resumes.urls')), 
    path('api/', include('jobs.urls')),
    path('api-auth/', include('rest_framework.urls')),

]
