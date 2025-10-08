"""
Forms for account settings.
"""
from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

from .settings_models import UserPreferences

User = get_user_model()


class PersonalInfoForm(forms.ModelForm):
    """Personal information form."""
    
    class Meta:
        model = UserPreferences
        fields = [
            'phone_number', 'bio', 'date_of_birth', 'gender',
            'language', 'timezone', 'currency'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
                'pattern': r'^\+?1?\d{9,15}$'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'maxlength': 500
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'language': forms.Select(attrs={
                'class': 'form-control'
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-control'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation
            phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_pattern.match(phone_number):
                raise ValidationError('Please enter a valid phone number.')
        return phone_number


class PasswordChangeForm(DjangoPasswordChangeForm):
    """Enhanced password change form."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })


class NotificationPreferencesForm(forms.ModelForm):
    """Notification preferences form."""
    
    class Meta:
        model = UserPreferences
        fields = [
            'email_notifications', 'sms_notifications', 'push_notifications',
            'order_updates', 'promotional_emails', 'newsletter',
            'product_recommendations', 'security_alerts'
        ]
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'toggleEmailNotifications()'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'toggleSMSNotifications()'
            }),
            'push_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order_updates': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'promotional_emails': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'newsletter': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'product_recommendations': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'security_alerts': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class SecurityQuestionForm(forms.ModelForm):
    """Security question form."""
    
    class Meta:
        model = UserPreferences
        fields = ['security_question', 'security_answer']
        widgets = {
            'security_question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your security question'
            }),
            'security_answer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your answer'
            })
        }


class PhoneVerificationForm(forms.Form):
    """Phone verification form."""
    
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number',
            'pattern': r'^\+?1?\d{9,15}$'
        })
    )
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_pattern.match(phone_number):
                raise ValidationError('Please enter a valid phone number.')
        return phone_number


class EmailChangeForm(forms.Form):
    """Email change form."""
    
    new_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new email address'
        })
    )
    confirm_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new email address'
        })
    )
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email')
        confirm_email = cleaned_data.get('confirm_email')
        current_password = cleaned_data.get('current_password')
        
        if new_email and confirm_email and new_email != confirm_email:
            raise ValidationError('Email addresses do not match.')
        
        if current_password and not self.user.check_password(current_password):
            raise ValidationError('Current password is incorrect.')
        
        if new_email and User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise ValidationError('This email address is already in use.')
        
        return cleaned_data


class AccountDeactivationForm(forms.Form):
    """Account deactivation form."""
    
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us why you\'re deactivating your account (optional)'
        }),
        required=False
    )
    confirm_deactivation = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I understand that deactivating my account will prevent me from logging in and accessing my data.'
    )


class AccountDeletionForm(forms.Form):
    """Account deletion form."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm deletion'
        })
    )
    confirm_deletion = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I understand that deleting my account is permanent and cannot be undone.'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and not self.user.check_password(password):
            raise ValidationError('Incorrect password.')
        return password


class ProfilePictureForm(forms.Form):
    """Profile picture upload form."""
    
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Check file size (max 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError('Image file too large. Maximum size is 5MB.')
            
            # Check file type
            if not picture.content_type.startswith('image/'):
                raise ValidationError('Please upload a valid image file.')
        
        return picture
