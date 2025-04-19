from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
)

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include([
        path('', include(router.urls)),
        path('', include('accounts.urls')),
        path('resumes/', include('resumes.urls')),
        path('jobs/', include('jobs.urls')),
        
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ])),
    
    path('api-auth/', include('rest_framework.urls')),
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)