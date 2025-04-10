from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'jobs', views.JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]