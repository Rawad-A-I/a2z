"""
Test product functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, Category, ProductVariant, ProductBundle, BundleItem
from accounts.models import Profile


class ProductTestCase(TestCase):
    """Test product features."""
    
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
            stock_quantity=100,
            low_stock_threshold=10
        )
    
    def test_product_creation(self):
        """Test product creation."""
        self.assertTrue(Product.objects.filter(product_name='Test Product').exists())
        self.assertEqual(self.product.stock_quantity, 100)
        self.assertEqual(self.product.low_stock_threshold, 10)
    
    def test_product_variants(self):
        """Test product variants."""
        variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001',
            size='M',
            color='Red',
            price_adjustment=5.00,
            stock_quantity=50
        )
        
        self.assertTrue(variant.is_in_stock())
        self.assertEqual(variant.get_price(), 104.99)  # Base price + adjustment
    
    def test_product_bundles(self):
        """Test product bundles."""
        bundle = ProductBundle.objects.create(
            name='Test Bundle',
            description='Test bundle description',
            discount_percentage=10.0
        )
        
        BundleItem.objects.create(
            bundle=bundle,
            product=self.product,
            quantity=2
        )
        
        self.assertEqual(bundle.bundle_items.count(), 1)
        self.assertEqual(bundle.get_bundle_price(), 179.98)  # 2 * 99.99 * 0.9
    
    def test_stock_management(self):
        """Test stock management."""
        initial_stock = self.product.stock_quantity
        self.product.update_stock(-10)
        self.assertEqual(self.product.stock_quantity, initial_stock - 10)
        self.assertTrue(self.product.is_in_stock())
    
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
    
    def test_order_fulfillment(self):
        """Test order fulfillment capability."""
        self.assertTrue(self.product.can_fulfill_order(50))
        self.assertFalse(self.product.can_fulfill_order(150))
    
    def test_product_rating(self):
        """Test product rating calculation."""
        # This would require ProductReview model implementation
        rating = self.product.get_rating()
        self.assertEqual(rating, 0)  # No reviews yet
