from django.urls import path
from django.shortcuts import redirect
from . import views
from .health import health_check, readiness_check, liveness_check

urlpatterns = [
    # Health check endpoints (for Railway)
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('live/', liveness_check, name='liveness_check'),
    
    # Main redirect homepage - entry point for all platforms
    path('', views.redirect_homepage, name='redirect_homepage'),
    
    # Platform-specific pages
    path('a2z-mart/', views.index, name='index'),  # Main e-commerce site with hero
    path('a2z-mart/products/', views.products_only, name='products_only'),  # Products only view
    path('a2z-bar/', lambda request: redirect('/products/bar/'), name='a2z_bar_redirect'),  # Redirect to new bar system
    path('rayan-brayan/', views.rayan_brayan, name='rayan_brayan'),  # Rayan O Brayan community
    
    # Other pages
    path('search/', views.product_search, name='product_search'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms_and_conditions, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('demo/', views.demo_design_system, name='demo_design_system'),
]