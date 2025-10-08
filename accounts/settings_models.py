"""
Account settings and user preferences models.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import BaseModel
import uuid


class UserPreferences(BaseModel):
    """User preferences and settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=500)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], blank=True, null=True)
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # Email notification types
    order_updates = models.BooleanField(default=True)
    promotional_emails = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=True)
    product_recommendations = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    
    # Privacy Settings
    profile_visibility = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private')
    ], default='private')
    show_online_status = models.BooleanField(default=True)
    allow_friend_requests = models.BooleanField(default=True)
    
    # Language and Region
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=3, default='USD')
    
    # Marketing Preferences
    marketing_consent = models.BooleanField(default=False)
    data_processing_consent = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s preferences"


class UserSession(BaseModel):
    """Track user sessions for security management."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('other', 'Other')
    ], default='desktop')
    browser = models.CharField(max_length=50, blank=True, null=True)
    operating_system = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name or 'Unknown Device'}"


class TwoFactorAuth(BaseModel):
    """Two-factor authentication settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=20, choices=[
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('app', 'Authenticator App')
    ], blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    last_used = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - 2FA {'Enabled' if self.is_enabled else 'Disabled'}"


class ConnectedAccount(BaseModel):
    """Connected social media accounts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connected_accounts')
    provider = models.CharField(max_length=20, choices=[
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('apple', 'Apple'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn')
    ])
    provider_id = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    connected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'provider']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.title()}"


class AccountActivity(BaseModel):
    """Track important account activities for security."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=[
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Changed'),
        ('email_change', 'Email Changed'),
        ('phone_change', 'Phone Changed'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('account_created', 'Account Created'),
        ('profile_updated', 'Profile Updated'),
        ('security_question_changed', 'Security Question Changed')
    ])
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class SecurityQuestion(BaseModel):
    """Security questions for account recovery."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_question')
    question = models.CharField(max_length=200)
    answer_hash = models.CharField(max_length=255)  # Hashed answer
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - Security Question"


class EmailVerification(BaseModel):
    """Email verification tokens."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.user.username} - {self.email} verification"


class PhoneVerification(BaseModel):
    """Phone verification codes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_verifications')
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_max_attempts_reached(self):
        return self.attempts >= 3
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number} verification"
