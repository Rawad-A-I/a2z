from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from accounts.models import Profile
from home.models import ShippingAddress


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image', 'bio', 'phone_number', 'phone_country_code']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'required': True,
                'inputmode': 'numeric',
                'pattern': '[0-9]*'
            }),
            'phone_country_code': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].required = True
        self.fields['phone_country_code'].required = True
        
        # Add country code choices
        self.fields['phone_country_code'].choices = [
            ('+961', '+961 (Lebanon)'),
            ('+1', '+1 (USA/Canada)'),
            ('+44', '+44 (UK)'),
            ('+33', '+33 (France)'),
            ('+49', '+49 (Germany)'),
            ('+39', '+39 (Italy)'),
            ('+34', '+34 (Spain)'),
            ('+61', '+61 (Australia)'),
            ('+81', '+81 (Japan)'),
            ('+86', '+86 (China)'),
            ('+91', '+91 (India)'),
            ('+55', '+55 (Brazil)'),
            ('+52', '+52 (Mexico)'),
            ('+7', '+7 (Russia)'),
            ('+966', '+966 (Saudi Arabia)'),
            ('+971', '+971 (UAE)'),
            ('+20', '+20 (Egypt)'),
            ('+962', '+962 (Jordan)'),
            ('+90', '+90 (Turkey)'),
            ('+98', '+98 (Iran)'),
            ('+964', '+964 (Iraq)'),
            ('+965', '+965 (Kuwait)'),
            ('+974', '+974 (Qatar)'),
            ('+973', '+973 (Bahrain)'),
            ('+968', '+968 (Oman)'),
            ('+967', '+967 (Yemen)'),
            ('+970', '+970 (Palestine)'),
            ('+972', '+972 (Israel)'),
            ('+357', '+357 (Cyprus)'),
            ('+30', '+30 (Greece)'),
        ]
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        country_code = self.cleaned_data.get('phone_country_code', '+961')
        
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        if phone:
            # Remove all non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, phone))
            
            # Country-specific validation
            if country_code == '+961':  # Lebanon
                if len(digits_only) < 8 or len(digits_only) > 8:
                    raise forms.ValidationError("Lebanon phone number must be exactly 8 digits.")
            elif country_code == '+1':  # USA/Canada
                if len(digits_only) < 10 or len(digits_only) > 10:
                    raise forms.ValidationError("US/Canada phone number must be exactly 10 digits.")
            elif country_code in ['+44', '+33', '+49', '+39', '+34']:  # European countries
                if len(digits_only) < 9 or len(digits_only) > 12:
                    raise forms.ValidationError("Phone number must be between 9-12 digits for this country.")
            else:
                # General validation for other countries
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