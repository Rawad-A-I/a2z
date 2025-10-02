"""
Test customer experience functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, Wishlist, RecentlyViewed, ProductBundle, BundleItem
from products.models import Product, Category


class CustomerExperienceTestCase(TestCase):
    """Test customer experience features."""
    
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
        
        self.bundle = ProductBundle.objects.create(
            name='Test Bundle',
            description='Test bundle description',
            discount_percentage=10.0
        )
        
        BundleItem.objects.create(
            bundle=self.bundle,
            product=self.product,
            quantity=2
        )
    
    def test_wishlist_view(self):
        """Test wishlist view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_wishlist(self):
        """Test add to wishlist."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_to_wishlist', args=[self.product.uid]))
        self.assertEqual(response.status_code, 302)  # Redirect after adding
    
    def test_remove_from_wishlist(self):
        """Test remove from wishlist."""
        Wishlist.objects.create(user=self.user, product=self.product)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('remove_from_wishlist', args=[self.product.uid]))
        self.assertEqual(response.status_code, 302)  # Redirect after removal
    
    def test_wishlist_creation(self):
        """Test wishlist creation."""
        wishlist = Wishlist.objects.create(user=self.user, product=self.product)
        self.assertTrue(Wishlist.objects.filter(user=self.user, product=self.product).exists())
    
    def test_recently_viewed_view(self):
        """Test recently viewed view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recently_viewed'))
        self.assertEqual(response.status_code, 200)
    
    def test_track_product_view(self):
        """Test track product view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('track_product_view', args=[self.product.uid]))
        self.assertEqual(response.status_code, 200)
    
    def test_recently_viewed_creation(self):
        """Test recently viewed creation."""
        recently_viewed = RecentlyViewed.objects.create(user=self.user, product=self.product)
        self.assertTrue(RecentlyViewed.objects.filter(user=self.user, product=self.product).exists())
    
    def test_product_comparison_view(self):
        """Test product comparison view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('product_comparison'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_comparison(self):
        """Test add to comparison."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('product_comparison'), {
            'action': 'add',
            'product_id': str(self.product.uid)
        })
        self.assertEqual(response.status_code, 302)  # Redirect after adding
    
    def test_product_recommendations_view(self):
        """Test product recommendations view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('product_recommendations'))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_loyalty_view(self):
        """Test customer loyalty view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('customer_loyalty'))
        self.assertEqual(response.status_code, 200)
    
    def test_redeem_points(self):
        """Test redeem points."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('redeem_points'), {
            'points': 100
        })
        self.assertEqual(response.status_code, 302)  # Redirect after redemption
    
    def test_product_bundles_view(self):
        """Test product bundles view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('product_bundles'))
        self.assertEqual(response.status_code, 200)
    
    def test_bundle_detail_view(self):
        """Test bundle detail view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('bundle_detail', args=[self.bundle.uid]))
        self.assertEqual(response.status_code, 200)
    
    def test_add_bundle_to_cart(self):
        """Test add bundle to cart."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_bundle_to_cart', args=[self.bundle.uid]))
        self.assertEqual(response.status_code, 302)  # Redirect after adding
    
    def test_social_proof_api(self):
        """Test social proof API."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('social_proof', args=[self.product.uid]))
        self.assertEqual(response.status_code, 200)
    
    def test_personalized_homepage_view(self):
        """Test personalized homepage view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('personalized_homepage'))
        self.assertEqual(response.status_code, 200)
    
    def test_bundle_price_calculation(self):
        """Test bundle price calculation."""
        bundle_price = self.bundle.get_bundle_price()
        expected_price = (99.99 * 2) * 0.9  # 2 products with 10% discount
        self.assertEqual(bundle_price, expected_price)
