"""
Test CRM functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, CustomerLoyalty, CustomerSupport


class CRMTestCase(TestCase):
    """Test CRM features."""
    
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
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_customer_loyalty_creation(self):
        """Test customer loyalty creation."""
        self.assertTrue(CustomerLoyalty.objects.filter(user=self.user).exists())
        self.assertEqual(self.loyalty.tier, 'bronze')
        self.assertEqual(self.loyalty.points, 0)
    
    def test_loyalty_tier_update(self):
        """Test loyalty tier update."""
        self.loyalty.total_spent = 5000
        self.loyalty.update_tier()
        self.assertEqual(self.loyalty.tier, 'gold')
    
    def test_loyalty_points_addition(self):
        """Test loyalty points addition."""
        initial_points = self.loyalty.points
        self.loyalty.add_points(100)
        self.assertEqual(self.loyalty.points, initial_points + 1)
    
    def test_support_ticket_creation(self):
        """Test support ticket creation."""
        ticket = CustomerSupport.objects.create(
            user=self.user,
            subject='Test Issue',
            message='This is a test support ticket',
            priority='medium'
        )
        
        self.assertEqual(ticket.subject, 'Test Issue')
        self.assertEqual(ticket.status, 'open')
        self.assertEqual(ticket.priority, 'medium')
    
    def test_support_ticket_assignment(self):
        """Test support ticket assignment."""
        ticket = CustomerSupport.objects.create(
            user=self.user,
            subject='Test Issue',
            message='This is a test support ticket'
        )
        
        ticket.assigned_to = self.staff_user
        ticket.status = 'in_progress'
        ticket.save()
        
        self.assertEqual(ticket.assigned_to, self.staff_user)
        self.assertEqual(ticket.status, 'in_progress')
    
    def test_support_ticket_resolution(self):
        """Test support ticket resolution."""
        ticket = CustomerSupport.objects.create(
            user=self.user,
            subject='Test Issue',
            message='This is a test support ticket'
        )
        
        ticket.resolution = 'Issue resolved'
        ticket.status = 'resolved'
        ticket.save()
        
        self.assertEqual(ticket.resolution, 'Issue resolved')
        self.assertEqual(ticket.status, 'resolved')
    
    def test_crm_dashboard_access(self):
        """Test CRM dashboard access."""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('crm_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_list_view(self):
        """Test customer list view."""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('customer_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_detail_view(self):
        """Test customer detail view."""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('customer_detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_support_view(self):
        """Test customer support view."""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('customer_support'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_support_ticket(self):
        """Test creating support ticket."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('create_support_ticket'), {
            'subject': 'Test Issue',
            'message': 'This is a test support ticket',
            'priority': 'medium'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
    
    def test_my_support_tickets_view(self):
        """Test my support tickets view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_support_tickets'))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_segments_view(self):
        """Test customer segments view."""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('customer_segments'))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_analytics_view(self):
        """Test customer analytics view."""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('customer_analytics'))
        self.assertEqual(response.status_code, 200)
