from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.contrib.auth.models import User

from products.models import Product, Category, ProductReview
from accounts.models import Order, Cart, Profile, CustomerLoyalty
from .serializers import (
    ProductSerializer, CategorySerializer, ProductReviewSerializer,
    OrderSerializer, CartSerializer, ProfileSerializer, CustomerLoyaltySerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured', 'is_bestseller', 'is_new_arrival', 'is_in_stock']
    search_fields = ['product_name', 'product_desription', 'category__category_name']
    ordering_fields = ['price', 'created_at', 'product_name']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        """Add product to cart"""
        product = self.get_object()
        cart, created = Cart.objects.get_or_create(
            user=request.user, 
            is_paid=False
        )
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        return Response({'message': 'Product added to cart'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        """Add product to wishlist"""
        product = self.get_object()
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return Response({'message': 'Product added to wishlist'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Product already in wishlist'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def related_products(self, request, pk=None):
        """Get related products"""
        product = self.get_object()
        related = product.get_related_products()
        serializer = self.get_serializer(related, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        """Get bestseller products"""
        bestsellers = self.queryset.filter(is_bestseller=True)
        serializer = self.get_serializer(bestsellers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """Get new arrival products"""
        new_arrivals = self.queryset.filter(is_new_arrival=True)
        serializer = self.get_serializer(new_arrivals, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'stars']
    ordering_fields = ['date_added', 'stars']
    ordering = ['-date_added']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a review"""
        review = self.get_object()
        review.like_count += 1
        review.save()
        return Response({'like_count': review.like_count})

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        """Dislike a review"""
        review = self.get_object()
        review.dislike_count += 1
        review.save()
        return Response({'dislike_count': review.dislike_count})


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    ordering_fields = ['order_date', 'order_total_price']
    ordering = ['-order_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            order.save()
            return Response({'message': 'Order cancelled'})
        return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, is_paid=False)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Checkout cart"""
        cart = self.get_object()
        # Implement checkout logic here
        cart.is_paid = True
        cart.save()
        return Response({'message': 'Checkout successful'})


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomerLoyaltyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerLoyaltySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerLoyalty.objects.filter(user=self.request.user)
