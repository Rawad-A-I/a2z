from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from accounts.models import Profile
from home.models import ShippingAddress


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image', 'bio', 'phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'required': True,
                'inputmode': 'numeric',
                'pattern': '[0-9]*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].required = True
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        if phone:
            # Remove all non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, phone))
            
            # General validation - must be between 8-15 digits
            if len(digits_only) < 8 or len(digits_only) > 15:
                raise forms.ValidationError("Phone number must be between 8-15 digits.")
        
        return phone


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = '__all__'
        exclude = ['user']


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class AddressManagementForm(forms.ModelForm):
    """Form for managing user addresses with better validation"""
    class Meta:
        model = Profile
        fields = ['street_address', 'city', 'state', 'zip_code', 'country']
        widgets = {
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ZIP code'
            }),
            'country': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default country to Lebanon
        if not self.instance.country:
            self.fields['country'].initial = 'LB'
    
    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        country = self.cleaned_data.get('country', 'LB')
        
        if zip_code:
            # Country-specific validation
            if country == 'LB':
                # Lebanon postal codes are typically 4 digits
                if len(zip_code) < 4:
                    raise forms.ValidationError("Lebanon postal code must be at least 4 characters.")
            elif country == 'US':
                # US ZIP codes are 5 digits
                if len(zip_code) < 5:
                    raise forms.ValidationError("US ZIP code must be at least 5 characters.")
            elif country == 'CA':
                # Canadian postal codes are 6 characters (A1A 1A1 format)
                if len(zip_code) < 6:
                    raise forms.ValidationError("Canadian postal code must be at least 6 characters.")
            elif country == 'UK':
                # UK postal codes vary but typically 6-8 characters
                if len(zip_code) < 5:
                    raise forms.ValidationError("UK postal code must be at least 5 characters.")
            else:
                # General validation for other countries
                if len(zip_code) < 3:
                    raise forms.ValidationError("Postal code must be at least 3 characters.")
        return zip_code
    


class MultipleAddressForm(forms.ModelForm):
    """Form for managing multiple addresses"""
    class Meta:
        model = ShippingAddress
        fields = ['first_name', 'last_name', 'street', 'street_number', 'city', 'zip_code', 'country', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'street_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


# Account Settings Forms
from accounts.models import UserPreferences
import re


class PersonalInfoForm(forms.ModelForm):
    """Personal information form - A2Z Mart customized."""
    
    class Meta:
        model = UserPreferences
        fields = [
            'phone_number', 'bio', 'date_of_birth', 'gender',
            'language', 'timezone', 'currency', 'tax_rate',
            'age_verified', 'birth_date', 'dietary_restrictions',
            'preferred_delivery_method', 'product_categories',
            'preferred_contact_method', 'promotional_codes_enabled'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number (Lebanon: +961)',
                'pattern': r'^\+?961?\d{8}$'
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
            'birth_date': forms.DateInput(attrs={
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
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'age_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'dietary_restrictions': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'preferred_delivery_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'product_categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'promotional_codes_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # A2Z Mart specific choices
        self.fields['dietary_restrictions'].choices = [
            ('halal', 'Halal'),
            ('kosher', 'Kosher'),
            ('vegetarian', 'Vegetarian'),
            ('vegan', 'Vegan'),
            ('gluten_free', 'Gluten Free'),
            ('dairy_free', 'Dairy Free'),
            ('nut_free', 'Nut Free')
        ]
        
        self.fields['product_categories'].choices = [
            ('grocery', 'Grocery'),
            ('alcohol', 'Alcohol'),
            ('soft_drinks', 'Soft Drinks'),
            ('snacks', 'Snacks'),
            ('beverages', 'Beverages'),
            ('coffee', 'Coffee'),
            ('home_appliances', 'Home Appliances'),
            ('pet_food', 'Pet Food'),
            ('tobacco', 'Tobacco'),
            ('bakery', 'Bakery'),
            ('candy', 'Candy'),
            ('detergent', 'Detergent'),
            ('ice_cream', 'Ice Cream'),
            ('dairy', 'Dairy'),
            ('take_away', 'Take Away Drinks')
        ]
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Lebanon phone number validation
            phone_pattern = re.compile(r'^\+?961?\d{8}$')
            if not phone_pattern.match(phone_number):
                raise forms.ValidationError('Please enter a valid Lebanese phone number (e.g., +96170123456).')
        return phone_number
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            from datetime import date
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to purchase alcohol and tobacco products.')
        return birth_date


class PasswordChangeForm(forms.Form):
    """Enhanced password change form."""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Current password is incorrect.')
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('New passwords do not match.')
        
        return cleaned_data
    
    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user


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


class SecurityQuestionForm(forms.Form):
    """Security question form."""
    
    security_question = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your security question'
        })
    )
    security_answer = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your answer'
        })
    )


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
                raise forms.ValidationError('Please enter a valid phone number.')
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
            raise forms.ValidationError('Email addresses do not match.')
        
        if current_password and not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        
        if new_email and User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        
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
            raise forms.ValidationError('Incorrect password.')
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
                raise forms.ValidationError('Image file too large. Maximum size is 5MB.')
            
            # Check file type
            if not picture.content_type.startswith('image/'):
                raise forms.ValidationError('Please upload a valid image file.')
        
        return picture