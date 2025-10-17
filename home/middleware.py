from django.utils.deprecation import MiddlewareMixin
from django_user_agents.utils import get_user_agent

class MobileDetectionMiddleware(MiddlewareMixin):
    """Middleware to detect mobile devices and add to request"""
    
    def process_request(self, request):
        user_agent = get_user_agent(request)
        request.is_mobile = user_agent.is_mobile
        request.is_tablet = user_agent.is_tablet
        request.is_pc = user_agent.is_pc
        request.user_agent = user_agent
        return None
