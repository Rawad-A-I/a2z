"""
Custom middleware for rate limiting and security.
"""
import time
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings


class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent abuse.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip rate limiting for admin users
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)
            
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Rate limiting for login attempts
        if request.path == '/user/login/' and request.method == 'POST':
            if self.is_rate_limited(client_ip, 'login', 5, 300):  # 5 attempts per 5 minutes
                return HttpResponse("Too many login attempts. Please try again later.", status=429)
        
        # Rate limiting for registration
        if request.path == '/user/register/' and request.method == 'POST':
            if self.is_rate_limited(client_ip, 'register', 3, 600):  # 3 attempts per 10 minutes
                return HttpResponse("Too many registration attempts. Please try again later.", status=429)
        
        # General rate limiting
        if self.is_rate_limited(client_ip, 'general', 100, 60):  # 100 requests per minute
            return HttpResponse("Rate limit exceeded. Please slow down.", status=429)
            
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, client_ip, action, max_attempts, time_window):
        """Check if client is rate limited."""
        cache_key = f"rate_limit_{action}_{client_ip}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            return True
            
        cache.set(cache_key, attempts + 1, time_window)
        return False
