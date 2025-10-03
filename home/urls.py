from django.urls import path
from . import views
from .health import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health check endpoints (for Railway)
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('live/', liveness_check, name='liveness_check'),
    
    # Actual homepage and other pages
    path('', views.index, name='index'),
    path('search/', views.product_search, name='product_search'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms_and_conditions, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('a2z-bar/', views.a2z_bar, name='a2z_bar'),
    path('rayan-brayan/', views.rayan_brayan, name='rayan_brayan'),
]