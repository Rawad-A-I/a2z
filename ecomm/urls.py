from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Health check endpoints (for Railway)
    path('health/', include('home.urls')),
    path('ready/', include('home.urls')),
    path('live/', include('home.urls')),
    
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Home app - MINIMAL
    path('', include('home.urls')),
]

# Serve static files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)