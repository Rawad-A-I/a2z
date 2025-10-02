from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
import functools
import hashlib


def cache_result(timeout=None):
    """
    Decorator to cache function results
    """
    if timeout is None:
        timeout = getattr(settings, 'CACHE_TTL', 900)  # 15 minutes default
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate cache keys matching a pattern
    """
    # This is a simplified version - in production you might want to use Redis SCAN
    # For now, we'll just clear the entire cache when needed
    cache.clear()


class CacheMixin:
    """
    Mixin to add caching to ViewSets
    """
    cache_timeout = 900  # 15 minutes
    
    def get_cache_key(self, request):
        """Generate cache key for request"""
        key_parts = [
            self.__class__.__name__,
            request.method,
            request.path,
            str(request.GET.dict()),
            str(request.user.id) if request.user.is_authenticated else 'anonymous'
        ]
        return hashlib.md5('_'.join(key_parts).encode()).hexdigest()
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add caching"""
        if request.method == 'GET':
            cache_key = self.get_cache_key(request)
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
        
        response = super().dispatch(request, *args, **kwargs)
        
        if request.method == 'GET' and response.status_code == 200:
            cache_key = self.get_cache_key(request)
            cache.set(cache_key, response, self.cache_timeout)
        
        return response


def cache_product_list(timeout=900):
    """
    Cache decorator for product list views
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            cache_key = f"product_list_{hashlib.md5(str(request.GET.dict()).encode()).hexdigest()}"
            result = cache.get(cache_key)
            
            if result is None:
                result = view_func(request, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cache_product_detail(timeout=1800):
    """
    Cache decorator for product detail views
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, product_id, *args, **kwargs):
            cache_key = f"product_detail_{product_id}"
            result = cache.get(cache_key)
            
            if result is None:
                result = view_func(request, product_id, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator
