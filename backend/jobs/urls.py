
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from jobs.views import CompanyViewSet, JobViewSet


router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'job-listings', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
    # path('search/', JobSearchView.as_view(), name='job-search'),
    # path('stats/', JobStatisticsView.as_view(), name='job-stats'),
]