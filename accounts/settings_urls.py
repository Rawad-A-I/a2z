"""
URL patterns for account settings.
"""
from django.urls import path
from . import settings_views

urlpatterns = [
    # Main settings page
    path('settings/', settings_views.account_settings, name='account_settings'),
    
    # Personal Information
    path('settings/personal-information/', settings_views.personal_information, name='personal_information'),
    
    # Login & Security
    path('settings/login-security/', settings_views.login_security, name='login_security'),
    path('settings/change-password/', settings_views.change_password, name='change_password'),
    path('settings/revoke-session/<int:session_id>/', settings_views.revoke_session, name='revoke_session'),
    
    # Notification Preferences
    path('settings/notifications/', settings_views.notification_preferences, name='notification_preferences'),
    path('settings/update-notification-preference/', settings_views.update_notification_preference, name='update_notification_preference'),
    
    # Connected Accounts
    path('settings/connected-accounts/', settings_views.connected_accounts, name='connected_accounts'),
    path('settings/disconnect-account/<int:account_id>/', settings_views.disconnect_account, name='disconnect_account'),
    
    # Two-Factor Authentication
    path('settings/two-factor-setup/', settings_views.two_factor_setup, name='two_factor_setup'),
    path('settings/verify-phone-2fa/', settings_views.verify_phone_2fa, name='verify_phone_2fa'),
    
    # Danger Zone
    path('settings/danger-zone/', settings_views.danger_zone, name='danger_zone'),
    
    # Profile Picture
    path('settings/upload-profile-picture/', settings_views.upload_profile_picture, name='upload_profile_picture'),
    path('settings/delete-profile-picture/', settings_views.delete_profile_picture, name='delete_profile_picture'),
]
