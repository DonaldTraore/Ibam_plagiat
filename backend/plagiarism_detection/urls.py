"""
URL configuration for plagiarism_detection project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# API Info pour documentation simple
def api_info(request):
    return JsonResponse({
        "title": "Plagiarism Detection API",
        "version": "v1",
        "description": "API pour le système de détection de plagiat",
        "endpoints": {
            "auth": "/api/token/ (POST)",
            "refresh": "/api/token/refresh/ (POST)",
            "accounts": "/api/auth/",
            "reports": "/api/reports/",
            "themes": "/api/themes/",
            "history": "/api/history/",
            "notifications": "/api/notifications/",
            "documents": "/api/documents/",
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_info, name='api-info'),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Endpoints
    path('api/auth/', include('plagiarism_detection.accounts.urls')),
    path('api/reports/', include('plagiarism_detection.reports.urls')),
    path('api/themes/', include('plagiarism_detection.themes.urls')),
    path('api/history/', include('plagiarism_detection.history.urls')),
    path('api/notifications/', include('plagiarism_detection.notifications.urls')),
    path('api/documents/', include('plagiarism_detection.documents.urls')),
    path('api/', include('plagiarism_detection.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
