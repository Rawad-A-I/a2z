#!/usr/bin/env python3
"""
Django app for Railway - step-by-step integration
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')

# Initialize Django
django.setup()

# Get WSGI application
application = get_wsgi_application()

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'framework': 'Django'})

def readiness_check(request):
    """Readiness check endpoint"""
    return JsonResponse({'status': 'ready', 'framework': 'Django'})

def liveness_check(request):
    """Liveness check endpoint"""
    return JsonResponse({'status': 'alive', 'framework': 'Django'})

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
