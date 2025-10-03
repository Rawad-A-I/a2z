"""
Super simple health check for Railway deployment
No database required - just returns OK
"""
from django.http import JsonResponse

def health_check(request):
    """
    Simple health check that always returns OK
    No database or complex checks - just confirms app is running
    """
    return JsonResponse({'status': 'healthy'}, status=200)

def readiness_check(request):
    """
    Simple readiness check
    """
    return JsonResponse({'status': 'ready'}, status=200)

def liveness_check(request):
    """
    Simple liveness check
    """
    return JsonResponse({'status': 'alive'}, status=200)

