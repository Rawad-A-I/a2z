"""
Test order functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, Order, OrderItem, OrderFulfillment, Employee
from products.models import Product, Category


class OrderTestCase(TestCase):
    """Test order features."""
    
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
        
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='testpass123',
            is_staff=True
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
            user=self.user,
            order_id='TEST-001',
            payment_status='pending',
            shipping_address='123 Test St, Test City, TC 12345',
            payment_mode='COD',
            order_total_price=99.99,
            grand_total=99.99
        )
    
    def test_order_creation(self):
        """Test order creation."""
        self.assertTrue(Order.objects.filter(order_id='TEST-001').exists())
        self.assertEqual(self.order.status, 'pending')
    
    def test_order_item_creation(self):
        """Test order item creation."""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            product_price=99.99
        )
        
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.product_price, 99.99)
    
    def test_order_fulfillment_creation(self):
        """Test order fulfillment creation."""
        fulfillment = OrderFulfillment.objects.create(
            order=self.order,
            status='pending',
            shipping_method='Standard'
        )
        
        self.assertEqual(fulfillment.status, 'pending')
        self.assertEqual(fulfillment.shipping_method, 'Standard')
    
    def test_order_status_update(self):
        """Test order status update."""
        self.order.status = 'confirmed'
        self.order.save()
        self.assertEqual(self.order.status, 'confirmed')
    
    def test_order_assignment(self):
        """Test order assignment to employee."""
        self.order.assigned_employee = self.employee
        self.order.save()
        self.assertEqual(self.order.assigned_employee, self.employee)
    
    def test_fulfillment_status_update(self):
        """Test fulfillment status update."""
        fulfillment = OrderFulfillment.objects.create(
            order=self.order,
            status='pending'
        )
        
        fulfillment.status = 'shipped'
        fulfillment.tracking_number = 'TRACK123'
        fulfillment.save()
        
        self.assertEqual(fulfillment.status, 'shipped')
        self.assertEqual(fulfillment.tracking_number, 'TRACK123')
    
    def test_order_history_view(self):
        """Test order history view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('order_history'))
        self.assertEqual(response.status_code, 200)
    
    def test_order_details_view(self):
        """Test order details view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('order_details', args=[self.order.order_id]))
        self.assertEqual(response.status_code, 200)
    
    def test_employee_order_assignment(self):
        """Test employee order assignment."""
        self.client.login(username='employee', password='testpass123')
        response = self.client.post(reverse('assign_order', args=[self.order.order_id]), {
            'employee': self.employee.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after assignment
    
    def test_order_confirmation(self):
        """Test order confirmation."""
        self.client.login(username='employee', password='testpass123')
        response = self.client.post(reverse('confirm_order', args=[self.order.order_id]))
        self.assertEqual(response.status_code, 302)  # Redirect after confirmation
