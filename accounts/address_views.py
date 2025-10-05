"""
Address management with Google Maps integration.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests

from .models import Profile, StoreLocation


@login_required
def address_management(request):
    """Address management page with Google Maps."""
    profile = getattr(request.user, 'profile', None)
    
    if not profile:
        from .models import Profile
        profile = Profile.objects.create(user=request.user)
    
    # Get store locations for map
    store_locations = StoreLocation.objects.filter(is_active=True)
    
    context = {
        'profile': profile,
        'store_locations': store_locations,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'accounts/address_management.html', context)


@login_required
def update_shipping_address(request):
    """Update shipping address with Google Maps integration."""
    if request.method == 'POST':
        profile = getattr(request.user, 'profile', None)
        
        if not profile:
            from .models import Profile
            profile = Profile.objects.create(user=request.user)
        
        # Get address data from form
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country', 'US')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        # Update profile with new address
        profile.shipping_address = f"{address}, {city}, {state} {zip_code}, {country}"
        
        # Store individual address components
        profile.street_address = address
        profile.city = city
        profile.state = state
        profile.zip_code = zip_code
        profile.country = country
        
        # Store coordinates if provided
        if latitude and longitude:
            profile.latitude = latitude
            profile.longitude = longitude
        
        profile.save()
        
        messages.success(request, 'Shipping address updated successfully.')
        return redirect('address_management')
    
    return redirect('address_management')


@login_required
def geocode_address(request):
    """Geocode address using OpenStreetMap Nominatim with improved Lebanon support."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            address = data.get('address')
            country = data.get('country', 'LB')
            
            if not address:
                return JsonResponse({'error': 'Address is required'}, status=400)
            
            # OpenStreetMap Nominatim API
            base_url = getattr(settings, 'NOMINATIM_BASE_URL', 'https://nominatim.openstreetmap.org')
            user_agent = getattr(settings, 'NOMINATIM_USER_AGENT', 'Django-eCommerce-Website/1.0')
            
            url = f'{base_url}/search'
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': country.lower() if country != 'OTHER' else None,
                'bounded': 1 if country == 'LB' else 0  # Focus on Lebanon if selected
            }
            
            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}
            
            headers = {
                'User-Agent': user_agent
            }
            
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                location = {
                    'lat': float(result['lat']),
                    'lng': float(result['lon'])
                }
                
                # Parse address components for better accuracy
                address_components = result.get('address', {})
                parsed_components = {
                    'house_number': address_components.get('house_number', ''),
                    'road': address_components.get('road', ''),
                    'city': address_components.get('city') or address_components.get('town') or address_components.get('village', ''),
                    'state': address_components.get('state', ''),
                    'postcode': address_components.get('postcode', ''),
                    'country': address_components.get('country', '')
                }
                
                return JsonResponse({
                    'success': True,
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': result['display_name'],
                    'address_components': parsed_components
                })
            else:
                return JsonResponse({'error': 'Address not found. Please try a more specific address.'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def reverse_geocode(request):
    """Reverse geocode coordinates to address using OpenStreetMap Nominatim."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if not latitude or not longitude:
                return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)
            
            # OpenStreetMap Nominatim Reverse Geocoding API
            base_url = getattr(settings, 'NOMINATIM_BASE_URL', 'https://nominatim.openstreetmap.org')
            user_agent = getattr(settings, 'NOMINATIM_USER_AGENT', 'Django-eCommerce-Website/1.0')
            
            url = f'{base_url}/reverse'
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': user_agent
            }
            
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            if data and 'display_name' in data:
                return JsonResponse({
                    'success': True,
                    'formatted_address': data['display_name'],
                    'address_components': data.get('address', {})
                })
            else:
                return JsonResponse({'error': 'Location not found'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def find_nearby_stores(request):
    """Find nearby stores using Google Maps."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            radius = data.get('radius', 10)  # Default 10km radius
            
            if not latitude or not longitude:
                return JsonResponse({'error': 'Location is required'}, status=400)
            
            # Get all store locations
            stores = StoreLocation.objects.filter(is_active=True)
            
            nearby_stores = []
            for store in stores:
                if store.latitude and store.longitude:
                    # Calculate distance (simplified)
                    distance = calculate_distance(
                        float(latitude), float(longitude),
                        float(store.latitude), float(store.longitude)
                    )
                    
                    if distance <= radius:
                        nearby_stores.append({
                            'id': str(store.uid),
                            'name': store.name,
                            'address': store.address,
                            'city': store.city,
                            'state': store.state,
                            'zip_code': store.zip_code,
                            'phone': store.phone,
                            'email': store.email,
                            'distance': round(distance, 2),
                            'latitude': float(store.latitude),
                            'longitude': float(store.longitude)
                        })
            
            # Sort by distance
            nearby_stores.sort(key=lambda x: x['distance'])
            
            return JsonResponse({
                'success': True,
                'stores': nearby_stores
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def store_locator(request):
    """Store locator page."""
    store_locations = StoreLocation.objects.filter(is_active=True)
    
    context = {
        'store_locations': store_locations,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'accounts/store_locator.html', context)


@login_required
def click_and_collect(request):
    """Click and collect - order online, pickup in-store."""
    if request.method == 'POST':
        # Get selected store
        store_id = request.POST.get('store_id')
        store = get_object_or_404(StoreLocation, uid=store_id)
        
        # Update order with pickup location
        # This would integrate with your order system
        messages.success(request, f'Order set for pickup at {store.name}')
        return redirect('cart')
    
    # Get available stores
    stores = StoreLocation.objects.filter(is_active=True)
    
    context = {
        'stores': stores,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'accounts/click_and_collect.html', context)


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers."""
    import math
    
    # Haversine formula
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance


@login_required
def delivery_estimate(request):
    """Calculate delivery estimate based on address."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if not latitude or not longitude:
                return JsonResponse({'error': 'Location is required'}, status=400)
            
            # Find nearest store
            stores = StoreLocation.objects.filter(is_active=True)
            nearest_store = None
            min_distance = float('inf')
            
            for store in stores:
                if store.latitude and store.longitude:
                    distance = calculate_distance(
                        float(latitude), float(longitude),
                        float(store.latitude), float(store.longitude)
                    )
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_store = store
            
            if nearest_store:
                # Calculate delivery estimate (simplified)
                if min_distance <= 5:
                    delivery_days = 1
                elif min_distance <= 20:
                    delivery_days = 2
                else:
                    delivery_days = 3
                
                return JsonResponse({
                    'success': True,
                    'delivery_days': delivery_days,
                    'nearest_store': {
                        'name': nearest_store.name,
                        'distance': round(min_distance, 2)
                    }
                })
            else:
                return JsonResponse({'error': 'No stores available'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
