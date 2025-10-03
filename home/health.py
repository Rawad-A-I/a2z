"""
Health check views for Railway deployment
Optimized for production environments
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Comprehensive health check endpoint for Railway
    Returns 200 OK if database is operational
    Cache check is optional (doesn't fail health check)
    """
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database connectivity (CRITICAL)
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            health_status['checks']['database'] = 'ok'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['checks']['database'] = 'error'
        health_status['status'] = 'unhealthy'
    
    # Check cache connectivity (OPTIONAL - won't fail health check)
    try:
        # Only test cache if it's configured (not using Django's dummy cache)
        cache_backend = settings.CACHES.get('default', {}).get('BACKEND', '')
        if 'dummy' not in cache_backend.lower():
            cache.set('health_check', 'ok', 10)
            cache_value = cache.get('health_check')
            if cache_value == 'ok':
                health_status['checks']['cache'] = 'ok'
            else:
                health_status['checks']['cache'] = 'warning'
        else:
            health_status['checks']['cache'] = 'not_configured'
    except Exception as e:
        # Cache errors are logged but don't affect health status
        logger.warning(f"Cache health check failed (non-critical): {e}")
        health_status['checks']['cache'] = 'unavailable'
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Simple readiness probe for Railway
    Returns 200 OK immediately to indicate service is ready
    """
    return JsonResponse({'status': 'ready'}, status=200)


def liveness_check(request):
    """
    Minimal liveness probe - just confirms the app is running
    No database or cache checks - just returns OK
    """
    return JsonResponse({'status': 'alive'}, status=200)

