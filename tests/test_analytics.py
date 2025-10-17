"""
Test analytics functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, Order, Analytics
from products.models import Product, Category


class AnalyticsTestCase(TestCase):
    """Test analytics features."""
    
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
            stock_quantity=100
        )
        
        self.order = Order.objects.create(
            user=self.user,
            order_id='TEST-001',
            payment_status='completed',
            shipping_address='123 Test St, Test City, TC 12345',
            payment_mode='COD',
            order_total_price=99.99,
            grand_total=99.99
        )
    
    def test_analytics_dashboard_access(self):
        """Test analytics dashboard access."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_sales_analytics_view(self):
        """Test sales analytics view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sales_analytics'))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_analytics_view(self):
        """Test customer analytics view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('customer_analytics'))
        self.assertEqual(response.status_code, 200)
    
    def test_product_analytics_view(self):
        """Test product analytics view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('product_analytics'))
        self.assertEqual(response.status_code, 200)
    
    def test_inventory_analytics_view(self):
        """Test inventory analytics view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('inventory_analytics'))
        self.assertEqual(response.status_code, 200)
    
    def test_real_time_analytics_view(self):
        """Test real-time analytics view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('real_time_analytics'))
        self.assertEqual(response.status_code, 200)
    
    def test_analytics_data_creation(self):
        """Test analytics data creation."""
        analytics = Analytics.objects.create(
            date='2024-01-01',
            metric_type='sales',
            value=99.99,
            metadata={'orders': 1}
        )
        
        self.assertEqual(analytics.metric_type, 'sales')
        self.assertEqual(analytics.value, 99.99)
    
    def test_export_analytics(self):
        """Test analytics export."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('export_analytics') + '?type=sales')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_custom_report_view(self):
        """Test custom report view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('custom_report'))
        self.assertEqual(response.status_code, 200)
    
    def test_custom_report_creation(self):
        """Test custom report creation."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('custom_report'), {
            'report_name': 'Test Report',
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
            'metrics': ['sales_revenue', 'order_count']
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
