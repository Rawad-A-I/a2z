from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product, Category
import uuid
import secrets


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to="profile", null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    phone_country_code = models.CharField(max_length=5, default='+961', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    
    # Address coordinates for mapping
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Address components for better organization
    street_address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, default='LB')
    
    def save(self, *args, **kwargs):
        # Check if the profile image is being updated and profile exists
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if old_profile.profile_image and old_profile.profile_image != self.profile_image:
                    # Delete old image file
                    old_profile.profile_image.delete(save=False)
            except Profile.DoesNotExist:
                pass

        super(Profile, self).save(*args, **kwargs)

    def get_cart_count(self):
        """Get cart count for authenticated users"""
        try:
            cart = Cart.objects.get(user=self.user, is_paid=False)
            return sum(item.quantity for item in cart.cart_items.all())
        except Cart.DoesNotExist:
            return 0


class CustomerLoyalty(BaseModel):
    """Customer loyalty and tier system"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="loyalty")
    points = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ], default='bronze')
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    join_date = models.DateTimeField(auto_now_add=True)
    last_purchase = models.DateTimeField(null=True, blank=True)
    
    def update_tier(self):
        """Update customer tier based on total spent"""
        if self.total_spent >= 10000:
            self.tier = 'platinum'
        elif self.total_spent >= 5000:
            self.tier = 'gold'
        elif self.total_spent >= 2000:
            self.tier = 'silver'
        else:
            self.tier = 'bronze'
        self.save()
    
    def add_points(self, amount):
        """Add loyalty points based on purchase amount"""
        points_earned = int(amount * 0.01)  # 1 point per dollar
        self.points += points_earned
        self.save()


class StoreLocation(BaseModel):
    """Physical store locations"""
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    store_hours = models.JSONField(default=dict, help_text="Store hours in JSON format")
    
    def __str__(self):
        return self.name


class InventoryAlert(BaseModel):
    """Inventory alerts for low stock"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    threshold = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    alert_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def check_alert(self):
        """Check if alert should be triggered"""
        if self.product.stock_quantity <= self.threshold and not self.alert_sent:
            self.alert_sent = True
            self.save()
            return True
        return False


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=20)
    discount_amount = models.IntegerField()
    minimum_amount = models.IntegerField()
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_code


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, help_text="Session key for anonymous users")
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    class Meta:
        # Using indexes instead of unique_together to handle NULL values properly
        indexes = [
            models.Index(fields=['user', 'is_paid'], name='cart_user_paid_idx'),
            models.Index(fields=['session_key', 'is_paid'], name='cart_session_paid_idx'),
        ]
        constraints = [
            # Partial unique constraints are handled via database migration (0031)
        ]

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        total_price = 0

        for cart_item in cart_items:
            total_price += cart_item.get_product_price()

        return total_price

    def get_cart_total_price_after_coupon(self):
        total = self.get_cart_total()

        if self.coupon and total >= self.coupon.minimum_amount:
            total -= self.coupon.discount_amount
                    
        return total


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey('products.ColorVariant', on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey('products.SizeVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)

    def get_product_price(self):
        price = self.product.price * self.quantity

        if self.color_variant:
            price += self.color_variant.price
            
        if self.size_variant:
            price += self.size_variant.price
        
        return price


class Employee(BaseModel):
    """Employee model for order management."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, default="Sales")
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    store_location = models.ForeignKey(StoreLocation, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            import random
            self.employee_id = f"EMP{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_id = models.CharField(max_length=100, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=100)
    shipping_address = models.TextField(blank=True, null=True)
    payment_mode = models.CharField(max_length=100)
    order_total_price = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Employee management fields
    assigned_employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_orders")
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    is_confirmed = models.BooleanField(default=False)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
    def get_order_total_price(self):
        return self.order_total_price


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey('products.SizeVariant', on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey('products.ColorVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        """Calculate total price for this order item"""
        return self.product_price * self.quantity
    
    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"


class OrderFulfillment(BaseModel):
    """Advanced order fulfillment tracking"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="fulfillment")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ], default='pending')
    tracking_number = models.CharField(max_length=100, blank=True)
    shipping_method = models.CharField(max_length=50, default="Standard")
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    carrier = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Fulfillment for {self.order.order_id}"


class ProductBundle(BaseModel):
    """Product bundles for 'buy together' offers"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    products = models.ManyToManyField(Product, through='BundleItem')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def get_bundle_price(self):
        """Calculate bundle price with discount"""
        total_price = sum(item.product.price * item.quantity for item in self.bundle_items.all())
        discount_amount = total_price * (self.discount_percentage / 100)
        return total_price - discount_amount


class BundleItem(BaseModel):
    """Items in a product bundle"""
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE, related_name="bundle_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.bundle.name} - {self.product.product_name} x {self.quantity}"


class Wishlist(BaseModel):
    """Customer wishlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


class RecentlyViewed(BaseModel):
    """Recently viewed products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recently_viewed")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.username} viewed {self.product.product_name}"


class CustomerSupport(BaseModel):
    """Customer support tickets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="support_tickets")
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], default='open')
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.uid} - {self.subject}"


class Analytics(BaseModel):
    """Analytics and reporting data"""
    date = models.DateField()
    metric_type = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ['date', 'metric_type']
    
    def __str__(self):
        return f"{self.date} - {self.metric_type}: {self.value}"


class BusinessFormSubmission(BaseModel):
    """
    Model to store business customization form submissions
    """
    # Basic Information
    company_name = models.CharField(max_length=200, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Branding
    primary_color = models.CharField(max_length=7, blank=True, null=True, help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, blank=True, null=True, help_text="Hex color code")
    logo = models.ImageField(upload_to="business_logos/", blank=True, null=True)
    
    # Business Details
    main_products = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    # Additional Information
    business_description = models.TextField(blank=True, null=True)
    target_audience = models.TextField(blank=True, null=True)
    special_requirements = models.TextField(blank=True, null=True)
    
    # Form metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
    ])
    
    # Admin notes
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_business_forms')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Business Form Submission'
        verbose_name_plural = 'Business Form Submissions'
    
    def __str__(self):
        return f"{self.company_name or 'Unknown Company'} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_processed(self):
        return self.status != 'pending'
    
    @property
    def days_since_submission(self):
        from django.utils import timezone
        return (timezone.now() - self.submitted_at).days


# Account Settings Models
class UserPreferences(BaseModel):
    """User preferences and settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=500)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], blank=True, null=True)
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # Email notification types
    order_updates = models.BooleanField(default=True)
    promotional_emails = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=True)
    product_recommendations = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    
    # Privacy Settings
    profile_visibility = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private')
    ], default='private')
    show_online_status = models.BooleanField(default=True)
    allow_friend_requests = models.BooleanField(default=True)
    
    # Language and Region (A2Z Mart Customization)
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('ar', 'العربية'),
        ('fr', 'Français')
    ])
    additional_languages = models.JSONField(default=list, blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Beirut')
    currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'US Dollar'),
        ('LBP', 'Lebanese Pound'),
        ('EUR', 'Euro')
    ])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=11.00)
    
    # A2Z Mart Business-Specific Fields
    # Age Verification for Alcohol/Tobacco
    age_verified = models.BooleanField(default=False)
    birth_date = models.DateField(blank=True, null=True)
    
    # Dietary Restrictions
    dietary_restrictions = models.JSONField(default=list, blank=True)
    
    # Delivery Preferences
    preferred_delivery_method = models.CharField(max_length=20, choices=[
        ('express', 'Express'),
        ('same_day', 'Same Day'),
        ('pickup', 'Pickup')
    ], default='express')
    
    # Product Category Preferences
    product_categories = models.JSONField(default=list, blank=True)
    
    # Communication Preferences
    preferred_contact_method = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone')
    ], default='email')
    
    # Promotional Preferences
    promotional_codes_enabled = models.BooleanField(default=True)
    first_order_discount_used = models.BooleanField(default=False)
    
    # Marketing Preferences
    marketing_consent = models.BooleanField(default=False)
    data_processing_consent = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s preferences"


class UserSession(BaseModel):
    """Track user sessions for security management."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('other', 'Other')
    ], default='desktop')
    browser = models.CharField(max_length=50, blank=True, null=True)
    operating_system = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name or 'Unknown Device'}"


class TwoFactorAuth(BaseModel):
    """Two-factor authentication settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=20, choices=[
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('app', 'Authenticator App')
    ], blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    last_used = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - 2FA {'Enabled' if self.is_enabled else 'Disabled'}"


class ConnectedAccount(BaseModel):
    """Connected social media accounts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connected_accounts')
    provider = models.CharField(max_length=20, choices=[
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('apple', 'Apple'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn')
    ])
    provider_id = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    connected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'provider']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.title()}"


class AccountActivity(BaseModel):
    """Track important account activities for security."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=[
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Changed'),
        ('email_change', 'Email Changed'),
        ('phone_change', 'Phone Changed'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('account_created', 'Account Created'),
        ('profile_updated', 'Profile Updated'),
        ('security_question_changed', 'Security Question Changed')
    ])
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class SecurityQuestion(BaseModel):
    """Security questions for account recovery."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_question')
    question = models.CharField(max_length=200)
    answer_hash = models.CharField(max_length=255)  # Hashed answer
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - Security Question"


class EmailVerification(BaseModel):
    """Email verification tokens."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.user.username} - {self.email} verification"


class PhoneVerification(BaseModel):
    """Phone verification codes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_verifications')
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_max_attempts_reached(self):
        return self.attempts >= 3
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number} verification"


# Close Cash models
class CloseCashSchema(BaseModel):
    """Detected schema per workbook and sheet (date)."""
    workbook = models.CharField(max_length=100)  # e.g., "Ahmad.xlsx"
    sheet_name = models.CharField(max_length=100)  # typically date label
    schema_json = models.JSONField(default=dict)  # field definitions
    version = models.CharField(max_length=20, default="v1")

    class Meta:
        unique_together = ["workbook", "sheet_name", "version"]
        indexes = [
            models.Index(fields=["workbook", "sheet_name"]),
        ]

    def __str__(self):
        return f"Schema {self.workbook} / {self.sheet_name} ({self.version})"


class CloseCashEntry(BaseModel):
    """One submission per user/sheet/date with arbitrary fields in JSON."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="close_cash_entries")
    workbook = models.CharField(max_length=100)
    sheet_name = models.CharField(max_length=100)
    entry_date = models.DateField()
    data_json = models.JSONField(default=dict)
    source_version = models.CharField(max_length=20, default="v1")

    class Meta:
        indexes = [
            models.Index(fields=["user", "entry_date"]),
            models.Index(fields=["workbook", "sheet_name"]),
        ]
        unique_together = [
            ("user", "workbook", "sheet_name", "entry_date", "source_version"),
        ]

    def __str__(self):
        return f"{self.user.username} {self.workbook} {self.sheet_name} {self.entry_date}"


class A2ZSnapshot(BaseModel):
    """Optional snapshot of the A to Z master workbook (for audit/history)."""
    snapshot_at = models.DateTimeField(auto_now_add=True)
    data_json = models.JSONField(default=dict)
    note = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ["-snapshot_at"]

    def __str__(self):
        return f"A2Z Snapshot {self.snapshot_at.isoformat()}"