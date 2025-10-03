"""
Minimal URL configuration for Railway deployment
Only health check endpoints - no complex apps
"""
from django.contrib import admin
from django.urls import path
from home.health import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health check endpoints (for Railway)
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('live/', liveness_check, name='liveness_check'),
    
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Simple home page
    path('', health_check, name='home'),
]
