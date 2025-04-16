from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include([
        path('', include(router.urls)),
        path('accounts/', include('accounts.urls')),
        path('resumes/', include('resumes.urls')),
        path('jobs/', include('jobs.urls')),
    ])),
    
    path('api-auth/', include('rest_framework.urls')),
    path('', RedirectView.as_view(url='/api/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

