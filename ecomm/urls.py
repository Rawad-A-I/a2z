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
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # Products app
    path('products/', include('products.urls')),
    
    # Accounts app
    path('accounts/', include('accounts.urls')),
    
    # Home app
    path('', include('home.urls')),
]

# Serve static and media files - Step 12
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)