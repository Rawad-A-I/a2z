"""
Test inventory management functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, InventoryAlert, StoreLocation
from products.models import Product, Category, StockMovement


class InventoryTestCase(TestCase):
    """Test inventory features."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        # Profile is automatically created by signal
        self.profile = self.user.profile
        
        self.category = Category.objects.create(
            category_name='Test Category',
            category_image='test.jpg'
        )
        
        self.product = Product.objects.create(
            product_name='Test Product',
            category=self.category,
            price=99.99,
            product_desription='Test product description',
            stock_quantity=100,
            low_stock_threshold=10
        )
        
        self.store = StoreLocation.objects.create(
            name='Test Store',
            address='123 Test St',
            city='Test City',
            state='TC',
            zip_code='12345',
            phone='(555) 123-4567',
            email='test@store.com'
        )
    
    def test_inventory_alert_creation(self):
        """Test inventory alert creation."""
        alert = InventoryAlert.objects.create(
            product=self.product,
            threshold=5
        )
        
        self.assertTrue(alert.check_alert())
        self.assertTrue(alert.alert_sent)
    
    def test_stock_movement_creation(self):
        """Test stock movement creation."""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='in',
            quantity=50,
            reason='Restock',
            user=self.user
        )
        
        self.assertEqual(movement.quantity, 50)
        self.assertEqual(movement.movement_type, 'in')
    
    def test_stock_update(self):
        """Test stock update."""
        initial_stock = self.product.stock_quantity
        self.product.update_stock(-10)
        self.assertEqual(self.product.stock_quantity, initial_stock - 10)
    
    def test_low_stock_detection(self):
        """Test low stock detection."""
        self.product.stock_quantity = 5
        self.product.save()
        self.assertTrue(self.product.is_low_stock())
    
    def test_out_of_stock_detection(self):
        """Test out of stock detection."""
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock())
    
    def test_store_location_creation(self):
        """Test store location creation."""
        self.assertTrue(StoreLocation.objects.filter(name='Test Store').exists())
        self.assertEqual(self.store.city, 'Test City')
    
    def test_inventory_dashboard_access(self):
        """Test inventory dashboard access."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('inventory_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_stock_movements_view(self):
        """Test stock movements view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stock_movements'))
        self.assertEqual(response.status_code, 200)
    
    def test_stock_alerts_view(self):
        """Test stock alerts view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stock_alerts'))
        self.assertEqual(response.status_code, 200)
    
    def test_store_locations_view(self):
        """Test store locations view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('store_locations'))
        self.assertEqual(response.status_code, 200)
    
    def test_bulk_stock_update(self):
        """Test bulk stock update."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('bulk_stock_update'), {
            'updates': [{
                'product_id': str(self.product.uid),
                'movement_type': 'in',
                'quantity': 50,
                'reason': 'Bulk restock'
            }]
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
