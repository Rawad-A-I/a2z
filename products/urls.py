from django.urls import path
from products.views import *
from products.employee_views import *
from products.bar_views import *

urlpatterns = [
    path('', product_list, name='product_list'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<uid>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/move_to_cart/<uid>/', move_to_cart, name='move_to_cart'),
    path('wishlist/remove/<uid>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('product-reviews/', product_reviews, name='product_reviews'),
    path('product-reviews/edit/<uuid:review_uid>/', edit_review, name='edit_review'),
    path('like-review/<review_uid>/', like_review, name='like_review'),
    path('dislike-review/<review_uid>/',dislike_review, name='dislike_review'),
    path('add-review/<slug>/', add_review, name='add_review'),
    
    # Bar section URLs (must come before generic slug pattern)
    path('bar/', bar_home, name='bar_home'),
    path('bar/products/', bar_products, name='bar_products'),
    path('bar/product/<slug>/', bar_product_detail, name='bar_product_detail'),
    path('bar/categories/', bar_categories, name='bar_categories'),
    path('bar/add-to-cart/<uuid:product_id>/', add_to_bar_cart, name='add_to_bar_cart'),
    
    # Employee product management URLs
    path('employee/manage/', employee_product_management, name='employee_product_management'),
    path('employee/analytics/', product_analytics, name='product_analytics'),
    path('employee/add-product/', add_product, name='add_product'),
    path('employee/quick-edit/<uuid:product_id>/', quick_edit_product, name='quick_edit_product'),
    path('employee/bulk-actions/', bulk_product_actions, name='bulk_product_actions'),
    path('employee/barcode-management/<uuid:product_id>/', product_barcode_management, name='product_barcode_management'),
    path('employee/bulk-barcode/', bulk_barcode_upload, name='bulk_barcode_upload'),
    path('employee/barcode-search/', barcode_search, name='barcode_search'),
    path('employee/delete-barcode/<uuid:barcode_id>/', delete_barcode, name='delete_barcode'),
    
    # Generic product slug pattern (must be last)
    path('<slug>/', get_product, name='get_product'),
    path('<slug>/<review_uid>/delete/', delete_review, name='delete_review'),
]
