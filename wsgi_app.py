#!/usr/bin/env python3
"""
WSGI app for Django on Railway
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')

# Initialize Django
django.setup()

# Run migrations
print("Running database migrations...")
try:
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("Migrations completed successfully")
except Exception as e:
    print(f"Migration error: {e}")

# Collect static files
print("Collecting static files...")
try:
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
    print("Static files collected successfully")
except Exception as e:
    print(f"Static collection error: {e}")

# Get WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    execute_from_command_line(sys.argv)