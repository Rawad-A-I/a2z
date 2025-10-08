"""
Account settings views for both website and web app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import uuid
import hashlib
import secrets
from datetime import timedelta

from .models import Profile
from .settings_models import (
    UserPreferences, UserSession, TwoFactorAuth, ConnectedAccount,
    AccountActivity, SecurityQuestion, EmailVerification, PhoneVerification
)
from .forms import (
    PersonalInfoForm, PasswordChangeForm, NotificationPreferencesForm,
    SecurityQuestionForm, PhoneVerificationForm
)


@login_required
def account_settings(request):
    """Main account settings page - detects if mobile/webapp."""
    # Check if user is on mobile/webapp
    is_mobile = request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    
    if is_mobile:
        return render(request, 'accounts/settings/mobile_settings.html')
    else:
        return render(request, 'accounts/settings/website_settings.html')


@login_required
def personal_information(request):
    """Personal information settings."""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, request.FILES, instance=preferences)
        if form.is_valid():
            form.save()
            
            # Log activity
            AccountActivity.objects.create(
                user=request.user,
                activity_type='profile_updated',
                description='Personal information updated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Personal information updated successfully!')
            return redirect('personal_information')
    else:
        form = PersonalInfoForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/personal_information.html', context)


@login_required
def login_security(request):
    """Login and security settings."""
    # Get user sessions
    sessions = UserSession.objects.filter(user=request.user, is_active=True).order_by('-last_activity')
    
    # Get 2FA status
    two_factor, created = TwoFactorAuth.objects.get_or_create(user=request.user)
    
    # Get connected accounts
    connected_accounts = ConnectedAccount.objects.filter(user=request.user)
    
    # Get recent security activities
    activities = AccountActivity.objects.filter(
        user=request.user,
        activity_type__in=['login', 'password_change', 'email_change', '2fa_enabled', '2fa_disabled']
    ).order_by('-created_at')[:10]
    
    context = {
        'sessions': sessions,
        'two_factor': two_factor,
        'connected_accounts': connected_accounts,
        'activities': activities,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/login_security.html', context)


@login_required
@require_POST
def change_password(request):
    """Change user password."""
    form = PasswordChangeForm(request.user, request.POST)
    
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        
        # Log activity
        AccountActivity.objects.create(
            user=request.user,
            activity_type='password_change',
            description='Password changed successfully',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, 'Password changed successfully!')
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required
@require_POST
def revoke_session(request, session_id):
    """Revoke a specific session."""
    session = get_object_or_404(UserSession, id=session_id, user=request.user)
    session.is_active = False
    session.save()
    
    # Log activity
    AccountActivity.objects.create(
        user=request.user,
        activity_type='logout',
        description=f'Session revoked for {session.device_name or "Unknown Device"}',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    messages.success(request, 'Session revoked successfully!')
    return redirect('login_security')


@login_required
def notification_preferences(request):
    """Notification preferences settings."""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated!')
            return redirect('notification_preferences')
    else:
        form = NotificationPreferencesForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/notification_preferences.html', context)


@login_required
@require_POST
def update_notification_preference(request):
    """Update notification preference via AJAX."""
    preference = request.POST.get('preference')
    value = request.POST.get('value') == 'true'
    
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if hasattr(preferences, preference):
        setattr(preferences, preference, value)
        preferences.save()
        
        return JsonResponse({'success': True, 'value': value})
    
    return JsonResponse({'success': False, 'error': 'Invalid preference'})


@login_required
def connected_accounts(request):
    """Connected accounts management."""
    connected_accounts = ConnectedAccount.objects.filter(user=request.user)
    
    context = {
        'connected_accounts': connected_accounts,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/connected_accounts.html', context)


@login_required
@require_POST
def disconnect_account(request, account_id):
    """Disconnect a connected account."""
    account = get_object_or_404(ConnectedAccount, id=account_id, user=request.user)
    
    # Check if this is the primary account
    if account.is_primary:
        return JsonResponse({'success': False, 'error': 'Cannot disconnect primary account'})
    
    account.delete()
    
    # Log activity
    AccountActivity.objects.create(
        user=request.user,
        activity_type='profile_updated',
        description=f'Disconnected {account.provider.title()} account',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    messages.success(request, f'{account.provider.title()} account disconnected!')
    return redirect('connected_accounts')


@login_required
def two_factor_setup(request):
    """Setup two-factor authentication."""
    two_factor, created = TwoFactorAuth.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        method = request.POST.get('method')
        
        if method == 'sms':
            # Generate SMS verification code
            phone_number = request.POST.get('phone_number')
            if phone_number:
                # Create phone verification
                code = secrets.randbelow(900000) + 100000  # 6-digit code
                PhoneVerification.objects.create(
                    user=request.user,
                    phone_number=phone_number,
                    code=str(code),
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
                
                # TODO: Send SMS with code
                messages.info(request, f'Verification code sent to {phone_number}')
                return redirect('verify_phone_2fa')
        
        elif method == 'email':
            # Generate email verification
            token = uuid.uuid4()
            EmailVerification.objects.create(
                user=request.user,
                email=request.user.email,
                token=token,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            
            # TODO: Send email with verification link
            messages.info(request, 'Verification email sent!')
            return redirect('verify_email_2fa')
    
    context = {
        'two_factor': two_factor,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/two_factor_setup.html', context)


@login_required
def verify_phone_2fa(request):
    """Verify phone number for 2FA."""
    if request.method == 'POST':
        code = request.POST.get('code')
        verification = PhoneVerification.objects.filter(
            user=request.user,
            code=code,
            is_verified=False
        ).first()
        
        if verification and not verification.is_expired():
            verification.is_verified = True
            verification.save()
            
            # Enable 2FA
            two_factor, created = TwoFactorAuth.objects.get_or_create(user=request.user)
            two_factor.is_enabled = True
            two_factor.method = 'sms'
            two_factor.phone_number = verification.phone_number
            two_factor.save()
            
            # Log activity
            AccountActivity.objects.create(
                user=request.user,
                activity_type='2fa_enabled',
                description='Two-factor authentication enabled via SMS',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Two-factor authentication enabled!')
            return redirect('login_security')
        else:
            messages.error(request, 'Invalid or expired verification code!')
    
    return render(request, 'accounts/settings/verify_phone_2fa.html')


@login_required
def danger_zone(request):
    """Account deactivation and deletion."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'deactivate':
            # Deactivate account
            request.user.is_active = False
            request.user.save()
            
            # Log activity
            AccountActivity.objects.create(
                user=request.user,
                activity_type='profile_updated',
                description='Account deactivated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Account deactivated successfully!')
            return redirect('logout')
        
        elif action == 'delete':
            # Delete account
            password = request.POST.get('password')
            if request.user.check_password(password):
                # Log activity before deletion
                AccountActivity.objects.create(
                    user=request.user,
                    activity_type='profile_updated',
                    description='Account deleted',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                request.user.delete()
                messages.success(request, 'Account deleted successfully!')
                return redirect('index')
            else:
                messages.error(request, 'Incorrect password!')
    
    context = {
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/danger_zone.html', context)


@login_required
@require_POST
def upload_profile_picture(request):
    """Upload profile picture via AJAX."""
    if 'profile_picture' in request.FILES:
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        
        # Delete old picture if exists
        if preferences.profile_picture:
            default_storage.delete(preferences.profile_picture.name)
        
        # Save new picture
        preferences.profile_picture = request.FILES['profile_picture']
        preferences.save()
        
        return JsonResponse({
            'success': True,
            'url': preferences.profile_picture.url
        })
    
    return JsonResponse({'success': False, 'error': 'No file uploaded'})


@login_required
@require_POST
def delete_profile_picture(request):
    """Delete profile picture via AJAX."""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if preferences.profile_picture:
        default_storage.delete(preferences.profile_picture.name)
        preferences.profile_picture = None
        preferences.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'No profile picture to delete'})
