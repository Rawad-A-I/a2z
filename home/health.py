"""
Health check view for Railway deployment
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Comprehensive health check endpoint for Railway
    Returns 200 OK if all systems are operational
    """
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            health_status['checks']['database'] = 'ok'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['checks']['database'] = 'error'
        health_status['status'] = 'unhealthy'
    
    # Check cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'degraded'
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        health_status['checks']['cache'] = 'error'
        # Cache is not critical, don't mark as unhealthy
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Simple readiness check - just returns 200 OK
    Used by Railway to check if the service is ready to accept traffic
    """
    return JsonResponse({'status': 'ready'}, status=200)

