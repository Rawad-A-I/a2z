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
    
    # Products app - Step 3
    path('products/', include('products.urls')),
    
    # Home app
    path('', include('home.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)