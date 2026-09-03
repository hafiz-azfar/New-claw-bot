"""
URL routing for Al-Uloom Academy project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('aluloom.apps.users.urls_auth')),
    path('api/v1/', include('aluloom.apps.users.urls')),
    path('api/v1/', include('aluloom.apps.courses.urls')),
    path('api/v1/', include('aluloom.apps.live_sessions.urls')),
    path('api/v1/', include('aluloom.apps.recordings.urls')),
    path('api/v1/', include('aluloom.apps.messaging.urls')),
    path('api/v1/', include('aluloom.apps.certificates.urls')),
    path('api/v1/', include('aluloom.apps.enrollments.urls')),
    path('api/v1/', include('aluloom.apps.payments.urls')),
    path('api/v1/', include('aluloom.apps.email_campaigns.urls')),
    path('api/v1/', include('aluloom.apps.dashboard.urls')),
    
    # Webhooks
    path('webhooks/', include('aluloom.apps.payments.webhooks')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
