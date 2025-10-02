from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'reviews', views.ProductReviewViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'cart', views.CartViewSet)
router.register(r'profile', views.ProfileViewSet)
router.register(r'loyalty', views.CustomerLoyaltyViewSet)

# API Documentation
schema_view = get_schema_view(
    title="Django eCommerce API",
    description="Complete eCommerce API with products, orders, cart, and user management",
    version="1.0.0"
)

urlpatterns = [
    path('', include(router.urls)),
    path('schema/', schema_view, name='api-schema'),
    path('docs/', include_docs_urls(title='eCommerce API Documentation')),
    path('auth/', include('rest_framework.urls')),
]
