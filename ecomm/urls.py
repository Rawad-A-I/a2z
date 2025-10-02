from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('product/', include('products.urls')),

    # Custom user app (rename path to avoid conflict)
    path('user/', include('accounts.urls')),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # Search endpoints
    path('search/', include('search.urls')),
    
    # API Documentation
    path('api/schema/', include('drf_spectacular.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


urlpatterns += staticfiles_urlpatterns()
