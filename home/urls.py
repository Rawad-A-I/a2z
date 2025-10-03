from django.urls import path
# Demo comment: Health check endpoints are enabled for Railway deployment
from home.views import *
from home.health import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health check endpoints (for Railway and Kubernetes)
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('live/', liveness_check, name='liveness_check'),
    
    # Main pages
    path('', redirect_homepage, name="redirect_homepage"),
    path('mart/', index, name="index"),
    path('bar/', a2z_bar, name='a2z_bar'),
    path('rayan/', rayan_brayan, name='rayan_brayan'),
    path('search/', product_search, name='product_search'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('terms-and-conditions/', terms_and_conditions, name='terms-and-conditions'),
    path('privacy-policy/', privacy_policy, name='privacy-policy'),
]