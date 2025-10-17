"""
Test cart functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, Cart, CartItem, Coupon
from products.models import Product, Category


class CartTestCase(TestCase):
    """Test cart features."""
    
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
        
        self.cart = Cart.objects.create(user=self.user)
        self.coupon = Coupon.objects.create(
            coupon_code='TEST10',
            discount_amount=10,
            minimum_amount=50
        )
    
    def test_cart_creation(self):
        """Test cart creation."""
        self.assertTrue(Cart.objects.filter(user=self.user).exists())
    
    def test_add_to_cart(self):
        """Test adding product to cart."""
        response = self.client.post(reverse('add_to_cart', args=[self.product.uid]))
        self.assertEqual(response.status_code, 302)  # Redirect after adding to cart
    
    def test_cart_item_creation(self):
        """Test cart item creation."""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.get_product_price(), 199.98)
    
    def test_cart_total_calculation(self):
        """Test cart total calculation."""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        total = self.cart.get_cart_total()
        self.assertEqual(total, 199.98)
    
    def test_coupon_application(self):
        """Test coupon application."""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        self.cart.coupon = self.coupon
        self.cart.save()
        
        total_after_coupon = self.cart.get_cart_total_price_after_coupon()
        self.assertEqual(total_after_coupon, 89.99)  # 99.99 - 10
    
    def test_coupon_minimum_amount(self):
        """Test coupon minimum amount requirement."""
        # Create a product with price below minimum
        cheap_product = Product.objects.create(
            product_name='Cheap Product',
            category=self.category,
            price=30.00,
            product_desription='Cheap product',
            stock_quantity=100
        )
        
        CartItem.objects.create(
            cart=self.cart,
            product=cheap_product,
            quantity=1
        )
        
        self.cart.coupon = self.coupon
        self.cart.save()
        
        # Coupon should not apply due to minimum amount
        total_after_coupon = self.cart.get_cart_total_price_after_coupon()
        self.assertEqual(total_after_coupon, 30.00)  # No discount applied
    
    def test_cart_view(self):
        """Test cart view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
    
    def test_remove_from_cart(self):
        """Test removing item from cart."""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        response = self.client.post(reverse('remove_cart', args=[cart_item.uid]))
        self.assertEqual(response.status_code, 302)  # Redirect after removal
