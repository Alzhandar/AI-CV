from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'skills', views.SkillViewSet)
router.register(r'resumes', views.ResumeViewSet, basename='resume')
router.register(r'analysis', views.AnalysisHistoryViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]