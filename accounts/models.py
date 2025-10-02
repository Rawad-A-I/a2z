from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product, Category
import uuid


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
    date_of_birth = models.DateField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    
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
        return CartItem.objects.filter(cart__is_paid=False, cart__user=self.user).count()


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
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

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
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
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