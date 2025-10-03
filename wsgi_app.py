#!/usr/bin/env python3
"""
WSGI app for Django on Railway
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')

# Initialize Django
django.setup()

# Get WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
