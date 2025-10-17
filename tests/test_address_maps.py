"""
Test address and maps functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, StoreLocation


class AddressMapsTestCase(TestCase):
    """Test address and maps features."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Profile is automatically created by signal
        self.profile = self.user.profile
        
        self.store = StoreLocation.objects.create(
            name='Test Store',
            address='123 Test St',
            city='Test City',
            state='TC',
            zip_code='12345',
            phone='(555) 123-4567',
            email='test@store.com',
            latitude=40.7128,
            longitude=-74.0060
        )
    
    def test_address_management_view(self):
        """Test address management view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('address_management'))
        self.assertEqual(response.status_code, 200)
    
    def test_store_locator_view(self):
        """Test store locator view."""
        response = self.client.get(reverse('store_locator'))
        self.assertEqual(response.status_code, 200)
    
    def test_click_and_collect_view(self):
        """Test click and collect view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('click_and_collect'))
        self.assertEqual(response.status_code, 200)
    
    def test_store_location_creation(self):
        """Test store location creation."""
        self.assertTrue(StoreLocation.objects.filter(name='Test Store').exists())
        self.assertEqual(self.store.city, 'Test City')
        self.assertEqual(self.store.latitude, 40.7128)
        self.assertEqual(self.store.longitude, -74.0060)
    
    def test_geocode_address_api(self):
        """Test geocode address API."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('geocode_address'), {
            'address': '123 Main St, New York, NY 10001'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_reverse_geocode_api(self):
        """Test reverse geocode API."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('reverse_geocode'), {
            'latitude': 40.7128,
            'longitude': -74.0060
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_find_nearby_stores_api(self):
        """Test find nearby stores API."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('find_nearby_stores'), {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'radius': 10
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_delivery_estimate_api(self):
        """Test delivery estimate API."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delivery_estimate'), {
            'latitude': 40.7128,
            'longitude': -74.0060
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_update_shipping_address(self):
        """Test update shipping address."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('update_shipping_address'), {
            'address': '123 New St',
            'city': 'New City',
            'state': 'NC',
            'zip_code': '54321',
            'country': 'US'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
