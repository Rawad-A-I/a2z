from django.db import models
from django.utils.text import slugify
import uuid


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    category_image = models.ImageField(upload_to="catgories")
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.size_name


class ProductVariant(BaseModel):
    """Advanced product variants for size, color, material combinations"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=50, unique=True)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=30, blank=True)
    material = models.CharField(max_length=30, blank=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=50, blank=True)
    
    def get_price(self):
        """Get variant price including adjustments"""
        return self.product.price + self.price_adjustment
    
    def is_in_stock(self):
        """Check if variant is in stock"""
        return self.stock_quantity > 0
    
    def is_low_stock(self):
        """Check if variant is low on stock"""
        return self.stock_quantity <= self.product.low_stock_threshold
    
    def __str__(self):
        return f"{self.product.product_name} - {self.size} {self.color} {self.material}"


class Product(BaseModel):
    parent = models.ForeignKey(
        'self', related_name='child_products', on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.IntegerField()
    product_desription = models.TextField()
    color_variant = models.ManyToManyField(ColorVariant, blank=True)
    size_variant = models.ManyToManyField(SizeVariant, blank=True)
    newest_product = models.BooleanField(default=False)
    
    # Enhanced inventory management
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    is_in_stock = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in cm")
    
    # SEO and marketing
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    
    # Product features
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    
    # Product relationships
    related_products = models.ManyToManyField('self', blank=True, related_name="related_to")
    bundle_products = models.ManyToManyField('self', blank=True, related_name="bundled_with")
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.product_name

    def get_product_price_by_size(self, size):
        return self.price + SizeVariant.objects.get(size_name=size).price

    def get_rating(self):
        total = sum(int(review['stars']) for review in self.reviews.values())

        if self.reviews.count() > 0:
            return total / self.reviews.count()
        else:
            return 0
    
    def update_stock(self, quantity):
        """Update stock quantity and check if product is in stock."""
        self.stock_quantity = max(0, self.stock_quantity + quantity)
        self.is_in_stock = self.stock_quantity > 0
        self.save()
    
    def is_low_stock(self):
        """Check if product is low on stock."""
        return self.stock_quantity <= self.low_stock_threshold
    
    def can_fulfill_order(self, quantity):
        """Check if product can fulfill order quantity."""
        return self.stock_quantity >= quantity
    
    def get_variants(self):
        """Get all active variants for this product."""
        return self.variants.filter(is_active=True)
    
    def get_primary_variant(self):
        """Get the primary/default variant."""
        return self.variants.filter(is_active=True).first()
    
    def get_available_sizes(self):
        """Get all available sizes for this product."""
        return self.size_variant.all().distinct()
    
    def get_available_colors(self):
        """Get all available colors for this product."""
        return self.color_variant.all().distinct()
    
    def get_related_products(self, limit=4):
        """Get related products from same category."""
        return Product.objects.filter(
            category=self.category
        ).exclude(uid=self.uid)[:limit]
    
    def get_bundle_price(self):
        """Get bundle price if this product is part of a bundle."""
        bundles = ProductBundle.objects.filter(products=self)
        if bundles.exists():
            return bundles.first().get_bundle_price()
        return self.price


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to="product")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.product_name} - Image {self.sort_order}"


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="reviews")
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-date_added']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.stars} stars)"


class ProductComparison(BaseModel):
    """Product comparison feature"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="comparisons")
    products = models.ManyToManyField(Product, related_name="comparisons")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Comparison {self.uid}"


class ProductRecommendation(BaseModel):
    """AI-powered product recommendations"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="recommendations")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="recommendations")
    score = models.FloatField(default=0.0)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-score']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} (Score: {self.score})"


class StockMovement(BaseModel):
    """Track stock movements for inventory management"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    movement_type = models.CharField(max_length=20, choices=[
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage'),
    ])
    quantity = models.IntegerField()
    reason = models.CharField(max_length=200, blank=True)
    reference = models.CharField(max_length=100, blank=True)  # Order ID, PO number, etc.
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.product.product_name} - {self.movement_type} {self.quantity}"