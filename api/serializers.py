from rest_framework import serializers
from products.models import Product, Category, ProductReview, ProductImage
from accounts.models import Order, OrderItem, Cart, CartItem, Profile, CustomerLoyalty


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uid', 'category_name', 'category_image', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['uid', 'image', 'alt_text', 'is_primary', 'sort_order']


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['uid', 'stars', 'content', 'date_added', 'user_name', 'user_username', 
                 'is_verified_purchase', 'helpful_count', 'like_count', 'dislike_count']
        read_only_fields = ['uid', 'date_added', 'user_name', 'user_username']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['uid', 'product_name', 'slug', 'category', 'price', 'product_desription',
                 'stock_quantity', 'is_in_stock', 'is_low_stock', 'weight', 'dimensions',
                 'is_featured', 'is_bestseller', 'is_new_arrival', 'product_images',
                 'reviews', 'average_rating', 'review_count', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        return obj.get_rating()
    
    def get_review_count(self, obj):
        return obj.reviews.count()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_uid = serializers.CharField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['uid', 'product', 'product_uid', 'quantity', 'color_variant', 'size_variant']
        read_only_fields = ['uid']


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['uid', 'cart_items', 'total_price', 'item_count', 'is_paid', 'created_at']
        read_only_fields = ['uid', 'created_at']
    
    def get_total_price(self, obj):
        return obj.get_cart_total()
    
    def get_item_count(self, obj):
        return obj.cart_items.count()


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['uid', 'product', 'quantity', 'product_price', 'size_variant', 'color_variant']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    assigned_employee_name = serializers.CharField(source='assigned_employee.get_full_name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['uid', 'order_id', 'order_date', 'payment_status', 'shipping_address',
                 'payment_mode', 'order_total_price', 'grand_total', 'status', 'is_confirmed',
                 'confirmed_date', 'notes', 'order_items', 'user_name', 'assigned_employee_name']
        read_only_fields = ['uid', 'order_id', 'order_date']


class ProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['uid', 'user_name', 'user_email', 'profile_image', 'bio', 'shipping_address',
                 'phone_number', 'date_of_birth', 'is_email_verified', 'created_at']
        read_only_fields = ['uid', 'user_name', 'user_email', 'created_at']


class CustomerLoyaltySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = CustomerLoyalty
        fields = ['uid', 'user_name', 'points', 'tier', 'total_spent', 'join_date', 'last_purchase']
        read_only_fields = ['uid', 'user_name', 'join_date']
