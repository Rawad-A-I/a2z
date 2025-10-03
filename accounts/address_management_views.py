"""
Comprehensive address management system for customers.
Handles both Profile addresses and multiple ShippingAddress records.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import formset_factory

from .models import Profile, StoreLocation
from .forms import AddressManagementForm, MultipleAddressForm
from home.models import ShippingAddress


@login_required
def comprehensive_address_management(request):
    """Comprehensive address management page"""
    profile = getattr(request.user, 'profile', None)
    
    if not profile:
        profile = Profile.objects.create(user=request.user)
    
    # Get all user's shipping addresses
    shipping_addresses = ShippingAddress.objects.filter(user=request.user).order_by('-created_at')
    
    # Get store locations for map
    store_locations = StoreLocation.objects.filter(is_active=True)
    
    context = {
        'profile': profile,
        'shipping_addresses': shipping_addresses,
        'store_locations': store_locations,
    }
    
    return render(request, 'accounts/comprehensive_address_management.html', context)


@login_required
def update_profile_address(request):
    """Update profile address with enhanced features"""
    profile = getattr(request.user, 'profile', None)
    
    if not profile:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = AddressManagementForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Update the combined shipping_address field
            if profile.street_address and profile.city and profile.state:
                profile.shipping_address = f"{profile.street_address}, {profile.city}, {profile.state} {profile.zip_code}, {profile.country}"
            
            # Handle coordinates if provided
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if latitude and longitude:
                profile.latitude = latitude
                profile.longitude = longitude
            
            profile.save()
            
            messages.success(request, 'Address updated successfully!')
            return redirect('comprehensive_address_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddressManagementForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'accounts/update_profile_address.html', context)


@login_required
def add_shipping_address(request):
    """Add a new shipping address"""
    if request.method == 'POST':
        form = MultipleAddressForm(request.POST, user=request.user)
        if form.is_valid():
            # If this is set as current, unset others
            if request.POST.get('current_address'):
                ShippingAddress.objects.filter(user=request.user).update(current_address=False)
            
            shipping_address = form.save()
            
            if request.POST.get('current_address'):
                shipping_address.current_address = True
                shipping_address.save()
            
            messages.success(request, 'Shipping address added successfully!')
            return redirect('comprehensive_address_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MultipleAddressForm(user=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/add_shipping_address.html', context)


@login_required
def edit_shipping_address(request, address_id):
    """Edit an existing shipping address"""
    shipping_address = get_object_or_404(ShippingAddress, uid=address_id, user=request.user)
    
    if request.method == 'POST':
        form = MultipleAddressForm(request.POST, instance=shipping_address, user=request.user)
        if form.is_valid():
            # If this is set as current, unset others
            if request.POST.get('current_address'):
                ShippingAddress.objects.filter(user=request.user).update(current_address=False)
            
            shipping_address = form.save()
            
            if request.POST.get('current_address'):
                shipping_address.current_address = True
                shipping_address.save()
            
            messages.success(request, 'Shipping address updated successfully!')
            return redirect('comprehensive_address_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MultipleAddressForm(instance=shipping_address, user=request.user)
    
    context = {
        'form': form,
        'shipping_address': shipping_address,
    }
    
    return render(request, 'accounts/edit_shipping_address.html', context)


@login_required
def delete_shipping_address(request, address_id):
    """Delete a shipping address"""
    shipping_address = get_object_or_404(ShippingAddress, uid=address_id, user=request.user)
    
    if request.method == 'POST':
        shipping_address.delete()
        messages.success(request, 'Shipping address deleted successfully!')
        return redirect('comprehensive_address_management')
    
    context = {
        'shipping_address': shipping_address,
    }
    
    return render(request, 'accounts/delete_shipping_address.html', context)


@login_required
def set_default_address(request, address_id):
    """Set an address as the default/current address"""
    shipping_address = get_object_or_404(ShippingAddress, uid=address_id, user=request.user)
    
    # Unset all other addresses as current
    ShippingAddress.objects.filter(user=request.user).update(current_address=False)
    
    # Set this one as current
    shipping_address.current_address = True
    shipping_address.save()
    
    messages.success(request, f'Address set as default: {shipping_address}')
    return redirect('comprehensive_address_management')


@login_required
def address_validation(request):
    """Validate an address using external services"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            street = data.get('street', '')
            city = data.get('city', '')
            state = data.get('state', '')
            zip_code = data.get('zip_code', '')
            country = data.get('country', 'US')
            
            # Use Nominatim API for address validation
            from django.conf import settings
            import requests
            
            address_string = f"{street}, {city}, {state} {zip_code}, {country}"
            
            base_url = getattr(settings, 'NOMINATIM_BASE_URL', 'https://nominatim.openstreetmap.org')
            user_agent = getattr(settings, 'NOMINATIM_USER_AGENT', 'Django-eCommerce-Website/1.0')
            
            url = f'{base_url}/search'
            params = {
                'q': address_string,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {'User-Agent': user_agent}
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                return JsonResponse({
                    'valid': True,
                    'formatted_address': result['display_name'],
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon']),
                    'address_components': result.get('address', {})
                })
            else:
                return JsonResponse({
                    'valid': False,
                    'error': 'Address not found'
                })
                
        except Exception as e:
            return JsonResponse({
                'valid': False,
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
