from django.urls import path
from accounts.views import *
from accounts.employee_views import *
from accounts.inventory_views import *
from accounts.crm_views import *
from accounts.order_management_views import *
from accounts.customer_experience_views import *
from accounts.analytics_views import *
from accounts.address_views import *
from accounts.admin_views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    # User view urls with login, register, logout, and email activation.
    path('login/', login_page, name="login"),
    path('employee-login/', employee_login_page, name="employee_login"),
    path('register/', register_page, name="register"),
    path('logout/', user_logout, name='logout'),
    # Email verification disabled for simple setup
    # path('activate/<email_token>/', activate_email_account, name="activate_email"),
    # path('resend-verification/', resend_verification_email, name="resend_verification"),

    # Profile management urls with profile, change-password, and shipping-address
    path('profile/<str:username>/', profile_view, name='profile'),
    path('change-password/', change_password, name='change_password'),
    path('shipping-address/', update_shipping_address, name='shipping-address'),

    # Passoword reset urls with django default view.
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        html_email_template_name='registration/password_reset_email.html'), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Cart functionality with add-to-cart, update-cart, remove-cart, and remove-coupon urls.
    path('cart/', cart, name="cart"),
    path('add-to-cart/<uid>/', add_to_cart, name="add_to_cart"),
    path('update_cart_item/', update_cart_item, name='update_cart_item'),
    path('remove-cart/<uid>/', remove_cart, name="remove_cart"),
    path('remove-coupon/<cart_id>/', remove_coupon, name="remove_coupon"),

    # Order history and details urls
    path('order-history/', order_history, name='order_history'),
    path('order-details/<str:order_id>/', order_details, name='order_details'),
    path('order-tracking/<str:order_id>/', order_tracking, name='order_tracking'),
    path('order-details/<str:order_id>/download/', download_invoice, name='download_invoice'),

    # Delete user account url
    path('delete-account/', delete_account, name='delete_account'),
    
    # Employee URLs
    path('employee/dashboard/', employee_dashboard, name='employee_dashboard'),
    path('employee/order/<str:order_id>/', employee_order_detail, name='employee_order_detail'),
    path('employee/order/<str:order_id>/assign/', assign_order, name='assign_order'),
    path('employee/order/<str:order_id>/confirm/', confirm_order, name='confirm_order'),
    path('employee/order/<str:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('employee/order/<str:order_id>/cancel/', cancel_order, name='cancel_order'),
    
    # Inventory Management URLs
    path('inventory/dashboard/', inventory_dashboard, name='inventory_dashboard'),
    path('inventory/movements/', stock_movements, name='stock_movements'),
    path('inventory/update-stock/<product_id>/', update_stock, name='update_stock'),
    path('inventory/bulk-update/', bulk_stock_update, name='bulk_stock_update'),
    path('inventory/alerts/', stock_alerts, name='stock_alerts'),
    path('inventory/reports/', inventory_reports, name='inventory_reports'),
    path('inventory/locations/', store_locations, name='store_locations'),
    path('inventory/locations/edit/<location_id>/', edit_store_location, name='edit_store_location'),
    
    # CRM URLs
    path('crm/dashboard/', crm_dashboard, name='crm_dashboard'),
    path('crm/customers/', customer_list, name='customer_list'),
    path('crm/customers/<int:user_id>/', customer_detail, name='customer_detail'),
    path('crm/segments/', customer_segments, name='customer_segments'),
    path('crm/support/', customer_support, name='customer_support'),
    path('crm/support/ticket/<ticket_id>/', support_ticket_detail, name='support_ticket_detail'),
    path('crm/support/create/', create_support_ticket, name='create_support_ticket'),
    path('crm/support/my-tickets/', my_support_tickets, name='my_support_tickets'),
    path('crm/analytics/', customer_analytics, name='customer_analytics'),
    
    # Order Management URLs
    path('orders/dashboard/', order_management_dashboard, name='order_management_dashboard'),
    path('orders/list/', order_list, name='order_list'),
    path('orders/detail/<str:order_id>/', order_detail, name='order_detail'),
    path('orders/fulfillment/', fulfillment_center, name='fulfillment_center'),
    path('orders/pick-list/<str:order_id>/', pick_list, name='pick_list'),
    path('orders/update-fulfillment/<str:order_id>/', update_fulfillment_status, name='update_fulfillment_status'),
    path('orders/analytics/', order_analytics, name='order_analytics'),
    path('orders/bulk-actions/', bulk_order_actions, name='bulk_order_actions'),
    path('orders/returns/', order_returns, name='order_returns'),
    
    # Customer Experience URLs
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/add/<product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<product_id>/', move_to_cart, name='move_to_cart'),
    path('recently-viewed/', recently_viewed, name='recently_viewed'),
    path('track-view/<product_id>/', track_product_view, name='track_product_view'),
    path('compare/', product_comparison, name='product_comparison'),
    path('recommendations/', product_recommendations, name='product_recommendations'),
    path('quick-reorder/<str:order_id>/', quick_reorder, name='quick_reorder'),
    path('loyalty/', customer_loyalty, name='customer_loyalty'),
    path('loyalty/redeem/', redeem_points, name='redeem_points'),
    path('bundles/', product_bundles, name='product_bundles'),
    path('bundles/<bundle_id>/', bundle_detail, name='bundle_detail'),
    path('bundles/<bundle_id>/add-to-cart/', add_bundle_to_cart, name='add_bundle_to_cart'),
    path('social-proof/<product_id>/', social_proof, name='social_proof'),
    path('personalized-home/', personalized_homepage, name='personalized_homepage'),
    
    # Analytics URLs
    path('analytics/dashboard/', analytics_dashboard, name='analytics_dashboard'),
    path('analytics/sales/', sales_analytics, name='sales_analytics'),
    path('analytics/customers/', customer_analytics, name='customer_analytics'),
    path('analytics/products/', product_analytics, name='product_analytics'),
    path('analytics/inventory/', inventory_analytics, name='inventory_analytics'),
    path('analytics/export/', export_analytics, name='export_analytics'),
    path('analytics/custom-report/', custom_report, name='custom_report'),
    path('analytics/real-time/', real_time_analytics, name='real_time_analytics'),
    
    # Address Management URLs
    path('address/', address_management, name='address_management'),
    path('address/update/', update_shipping_address, name='update_shipping_address'),
    path('address/geocode/', geocode_address, name='geocode_address'),
    path('address/reverse-geocode/', reverse_geocode, name='reverse_geocode'),
    path('address/nearby-stores/', find_nearby_stores, name='find_nearby_stores'),
    path('store-locator/', store_locator, name='store_locator'),
    path('click-collect/', click_and_collect, name='click_and_collect'),
    path('delivery-estimate/', delivery_estimate, name='delivery_estimate'),
    
    # Admin URLs
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/users/', user_management, name='user_management'),
    path('admin/users/<int:user_id>/', user_detail, name='user_detail'),
    path('admin/users/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('admin/products/', product_management, name='product_management'),
    path('admin/products/<product_id>/', product_detail_admin, name='product_detail_admin'),
    path('admin/orders/', order_management_admin, name='order_management_admin'),
    path('admin/settings/', system_settings, name='system_settings'),
    path('admin/locations/', store_locations_admin, name='store_locations_admin'),
    path('admin/employees/', employee_management, name='employee_management'),
    path('admin/reports/', system_reports, name='system_reports'),
    path('admin/backup/', backup_restore, name='backup_restore'),
    path('admin/logs/', system_logs, name='system_logs'),
]