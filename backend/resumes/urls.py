from django.urls import path, include
from rest_framework.routers import DefaultRouter

from resumes.views import SkillViewSet, ResumeViewSet, AnalysisHistoryViewSet

router = DefaultRouter()

router.register(r'skills', SkillViewSet)
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'analysis', AnalysisHistoryViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]