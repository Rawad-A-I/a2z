from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home.health import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health check endpoints (for Railway) - direct imports
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('live/', liveness_check, name='liveness_check'),
    
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Products app
    path('products/', include('products.urls')),
    
    # Accounts app
    path('accounts/', include('accounts.urls')),
    
    # Home app (must be last to catch root path)
    path('', include('home.urls')),
]

# Serve static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production: serve media files through Django
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)