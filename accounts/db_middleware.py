"""
Database connection middleware for Railway
Handles database connection drops and retries
"""
import time
from django.db import connection
from django.db.utils import OperationalError
from django.core.exceptions import ImproperlyConfigured


class DatabaseConnectionMiddleware:
    """
    Middleware to handle database connection issues on Railway
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure database connection is alive
        try:
            connection.ensure_connection()
        except OperationalError:
            # If connection is dead, close it and let Django create a new one
            connection.close()
            connection.ensure_connection()
        
        response = self.get_response(request)
        return response
