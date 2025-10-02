"""
Test authentication functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, CustomerLoyalty


class AuthenticationTestCase(TestCase):
    """Test authentication features."""
    
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
        self.loyalty = CustomerLoyalty.objects.create(user=self.user)
    
    def test_user_registration(self):
        """Test user registration."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_login(self):
        """Test user login."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_user_logout(self):
        """Test user logout."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_profile_creation(self):
        """Test profile creation on user registration."""
        user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123'
        )
        self.assertTrue(Profile.objects.filter(user=user).exists())
    
    def test_loyalty_program_creation(self):
        """Test loyalty program creation."""
        user = User.objects.create_user(
            username='loyaltyuser',
            email='loyalty@example.com',
            password='testpass123'
        )
        self.assertTrue(CustomerLoyalty.objects.filter(user=user).exists())
    
    def test_loyalty_tier_update(self):
        """Test loyalty tier update based on spending."""
        self.loyalty.total_spent = 5000
        self.loyalty.update_tier()
        self.assertEqual(self.loyalty.tier, 'gold')
    
    def test_loyalty_points_addition(self):
        """Test loyalty points addition."""
        initial_points = self.loyalty.points
        self.loyalty.add_points(100)
        self.assertEqual(self.loyalty.points, initial_points + 1)  # 1 point per dollar
