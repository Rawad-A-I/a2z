from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from accounts.models import Profile
from home.models import ShippingAddress


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image', 'bio']


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
        fields = ['street_address', 'city', 'state', 'zip_code', 'country', 'phone_number']
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
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
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
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove all non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, phone))
            if len(digits_only) < 10:
                raise forms.ValidationError("Phone number must be at least 10 digits.")
        return phone


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