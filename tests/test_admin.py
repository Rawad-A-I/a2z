"""
Test admin functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, Order, Employee, StoreLocation
from products.models import Product, Category


class AdminTestCase(TestCase):
    """Test admin features."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        # Profile is automatically created by signal
        self.profile = self.admin_user.profile
        
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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
            user=self.regular_user,
            order_id='TEST-001',
            payment_status='completed',
            shipping_address='123 Test St, Test City, TC 12345',
            payment_mode='COD',
            order_total_price=99.99,
            grand_total=99.99
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
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_management_view(self):
        """Test user management view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_detail_view(self):
        """Test user detail view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('user_detail', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_user_view(self):
        """Test edit user view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('edit_user', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_user_post(self):
        """Test edit user POST."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('edit_user', args=[self.regular_user.id]), {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'is_active': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
    
    def test_product_management_view(self):
        """Test product management view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('product_management'))
        self.assertEqual(response.status_code, 200)
    
    def test_product_detail_admin_view(self):
        """Test product detail admin view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('product_detail_admin', args=[self.product.uid]))
        self.assertEqual(response.status_code, 200)
    
    def test_order_management_admin_view(self):
        """Test order management admin view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('order_management_admin'))
        self.assertEqual(response.status_code, 200)
    
    def test_system_settings_view(self):
        """Test system settings view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('system_settings'))
        self.assertEqual(response.status_code, 200)
    
    def test_store_locations_admin_view(self):
        """Test store locations admin view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('store_locations_admin'))
        self.assertEqual(response.status_code, 200)
    
    def test_employee_management_view(self):
        """Test employee management view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('employee_management'))
        self.assertEqual(response.status_code, 200)
    
    def test_employee_creation(self):
        """Test employee creation."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('employee_management'), {
            'username': 'newemployee',
            'email': 'employee@example.com',
            'first_name': 'New',
            'last_name': 'Employee',
            'department': 'Sales',
            'store_location': str(self.store.uid)
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
    
    def test_system_reports_view(self):
        """Test system reports view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('system_reports'))
        self.assertEqual(response.status_code, 200)
    
    def test_backup_restore_view(self):
        """Test backup restore view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('backup_restore'))
        self.assertEqual(response.status_code, 200)
    
    def test_system_logs_view(self):
        """Test system logs view."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('system_logs'))
        self.assertEqual(response.status_code, 200)
    
    def test_employee_creation_model(self):
        """Test employee creation model."""
        employee = Employee.objects.create(
            user=self.regular_user,
            department='Sales',
            store_location=self.store
        )
        
        self.assertTrue(Employee.objects.filter(user=self.regular_user).exists())
        self.assertEqual(employee.department, 'Sales')
        self.assertEqual(employee.store_location, self.store)
    
    def test_non_admin_access_denied(self):
        """Test non-admin access is denied."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden
