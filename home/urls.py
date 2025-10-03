from django.urls import path
from home.health import health_check, readiness_check, liveness_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('live/', liveness_check, name='liveness_check'),
    path('', health_check, name='home'),
]