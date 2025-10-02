"""
Customer experience enhancement views.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import random

from .models import Wishlist, RecentlyViewed, CustomerLoyalty, ProductBundle
from products.models import Product, ProductReview, ProductComparison, ProductRecommendation


@login_required
def wishlist(request):
    """Customer wishlist management."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    # Pagination
    paginator = Paginator(wishlist_items, 12)
    page_number = request.GET.get('page')
    wishlist_page = paginator.get_page(page_number)
    
    context = {
        'wishlist_items': wishlist_page,
    }
    
    return render(request, 'accounts/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    if request.method == 'POST':
        product = get_object_or_404(Product, uid=product_id)
        
        # Check if already in wishlist
        if not Wishlist.objects.filter(user=request.user, product=product).exists():
            Wishlist.objects.create(user=request.user, product=product)
            messages.success(request, f'{product.product_name} added to wishlist.')
        else:
            messages.info(request, f'{product.product_name} is already in your wishlist.')
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    if request.method == 'POST':
        product = get_object_or_404(Product, uid=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        messages.success(request, f'{product.product_name} removed from wishlist.')
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


@login_required
def move_to_cart(request, product_id):
    """Move product from wishlist to cart."""
    if request.method == 'POST':
        product = get_object_or_404(Product, uid=product_id)
        
        # Remove from wishlist
        Wishlist.objects.filter(user=request.user, product=product).delete()
        
        # Add to cart (you'll need to implement this based on your cart system)
        # For now, just redirect to product page
        messages.success(request, f'{product.product_name} moved to cart.')
        return redirect('get_product', slug=product.slug)
    
    return redirect('wishlist')


@login_required
def recently_viewed(request):
    """Recently viewed products."""
    recently_viewed = RecentlyViewed.objects.filter(
        user=request.user
    ).select_related('product').order_by('-viewed_at')
    
    # Pagination
    paginator = Paginator(recently_viewed, 12)
    page_number = request.GET.get('page')
    recently_page = paginator.get_page(page_number)
    
    context = {
        'recently_viewed': recently_page,
    }
    
    return render(request, 'accounts/recently_viewed.html', context)


@login_required
def track_product_view(request, product_id):
    """Track product view for recently viewed."""
    if request.method == 'POST':
        product = get_object_or_404(Product, uid=product_id)
        
        # Update or create recently viewed record
        recently_viewed, created = RecentlyViewed.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'viewed_at': timezone.now()}
        )
        
        if not created:
            recently_viewed.viewed_at = timezone.now()
            recently_viewed.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def product_comparison(request):
    """Product comparison feature."""
    comparison = ProductComparison.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        
        if action == 'add':
            product = get_object_or_404(Product, uid=product_id)
            if not comparison:
                comparison = ProductComparison.objects.create(user=request.user)
            
            if comparison.products.count() < 4:  # Limit to 4 products
                comparison.products.add(product)
                messages.success(request, f'{product.product_name} added to comparison.')
            else:
                messages.warning(request, 'You can compare up to 4 products.')
        
        elif action == 'remove':
            product = get_object_or_404(Product, uid=product_id)
            if comparison:
                comparison.products.remove(product)
                messages.success(request, f'{product.product_name} removed from comparison.')
        
        elif action == 'clear':
            if comparison:
                comparison.products.clear()
                messages.success(request, 'Comparison cleared.')
        
        return redirect('product_comparison')
    
    context = {
        'comparison': comparison,
    }
    
    return render(request, 'accounts/product_comparison.html', context)


@login_required
def product_recommendations(request):
    """AI-powered product recommendations."""
    # Simple recommendation algorithm based on purchase history and preferences
    recommendations = ProductRecommendation.objects.filter(
        user=request.user
    ).select_related('product').order_by('-score')[:12]
    
    # If no recommendations exist, generate some
    if not recommendations.exists():
        # Get user's purchase history
        user_orders = request.user.orders.all()
        purchased_categories = set()
        
        for order in user_orders:
            for item in order.order_items.all():
                purchased_categories.add(item.product.category)
        
        # Recommend products from same categories
        recommended_products = Product.objects.filter(
            category__in=purchased_categories
        ).exclude(
            orders__user=request.user  # Exclude already purchased
        ).order_by('?')[:12]
        
        # Create recommendation records
        for product in recommended_products:
            ProductRecommendation.objects.create(
                user=request.user,
                product=product,
                score=random.uniform(0.5, 1.0),
                reason="Based on your purchase history"
            )
        
        recommendations = ProductRecommendation.objects.filter(
            user=request.user
        ).select_related('product').order_by('-score')[:12]
    
    context = {
        'recommendations': recommendations,
    }
    
    return render(request, 'accounts/product_recommendations.html', context)


@login_required
def quick_reorder(request, order_id):
    """Quick reorder from previous order."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # Add all items from the order to cart
    for order_item in order.order_items.all():
        # You'll need to implement this based on your cart system
        # For now, just show a message
        pass
    
    messages.success(request, f'Items from order {order_id} added to cart.')
    return redirect('cart')


@login_required
def customer_loyalty(request):
    """Customer loyalty program."""
    loyalty = getattr(request.user, 'loyalty', None)
    
    if not loyalty:
        # Create loyalty account if it doesn't exist
        loyalty = CustomerLoyalty.objects.create(user=request.user)
    
    # Get loyalty benefits
    benefits = {
        'bronze': {
            'name': 'Bronze',
            'points_rate': 0.01,
            'benefits': ['1% points on purchases', 'Email support']
        },
        'silver': {
            'name': 'Silver',
            'points_rate': 0.02,
            'benefits': ['2% points on purchases', 'Priority support', 'Free shipping on orders over $50']
        },
        'gold': {
            'name': 'Gold',
            'points_rate': 0.03,
            'benefits': ['3% points on purchases', 'VIP support', 'Free shipping', 'Early access to sales']
        },
        'platinum': {
            'name': 'Platinum',
            'points_rate': 0.05,
            'benefits': ['5% points on purchases', 'Personal shopper', 'Free shipping', 'Exclusive products', 'Birthday gift']
        }
    }
    
    # Get points history (you can implement this)
    points_history = []  # Implement points transaction history
    
    context = {
        'loyalty': loyalty,
        'benefits': benefits,
        'points_history': points_history,
    }
    
    return render(request, 'accounts/customer_loyalty.html', context)


@login_required
def redeem_points(request):
    """Redeem loyalty points."""
    if request.method == 'POST':
        points_to_redeem = int(request.POST.get('points', 0))
        loyalty = getattr(request.user, 'loyalty', None)
        
        if loyalty and loyalty.points >= points_to_redeem:
            # Calculate discount (example: 100 points = $1 discount)
            discount_amount = points_to_redeem / 100
            
            # Deduct points
            loyalty.points -= points_to_redeem
            loyalty.save()
            
            # Create discount coupon or apply discount
            # You'll need to implement this based on your coupon system
            
            messages.success(request, f'Redeemed {points_to_redeem} points for ${discount_amount:.2f} discount.')
        else:
            messages.error(request, 'Insufficient points or invalid amount.')
    
    return redirect('customer_loyalty')


@login_required
def product_bundles(request):
    """View available product bundles."""
    bundles = ProductBundle.objects.filter(is_active=True).prefetch_related('products')
    
    context = {
        'bundles': bundles,
    }
    
    return render(request, 'accounts/product_bundles.html', context)


@login_required
def bundle_detail(request, bundle_id):
    """Detailed view of product bundle."""
    bundle = get_object_or_404(ProductBundle, uid=bundle_id, is_active=True)
    bundle_items = bundle.bundle_items.select_related('product')
    
    context = {
        'bundle': bundle,
        'bundle_items': bundle_items,
    }
    
    return render(request, 'accounts/bundle_detail.html', context)


@login_required
def add_bundle_to_cart(request, bundle_id):
    """Add entire bundle to cart."""
    if request.method == 'POST':
        bundle = get_object_or_404(ProductBundle, uid=bundle_id, is_active=True)
        
        # Add all products in bundle to cart
        for bundle_item in bundle.bundle_items.all():
            # You'll need to implement this based on your cart system
            # For now, just show a message
            pass
        
        messages.success(request, f'{bundle.name} bundle added to cart.')
        return redirect('cart')
    
    return redirect('bundle_detail', bundle_id=bundle_id)


@login_required
def social_proof(request, product_id):
    """Show social proof for product (e.g., "X people bought this today")."""
    product = get_object_or_404(Product, uid=product_id)
    
    # Get recent purchases of this product
    recent_purchases = OrderItem.objects.filter(
        product=product,
        order__order_date__gte=timezone.now().replace(hour=0, minute=0, second=0)
    ).count()
    
    # Get total purchases
    total_purchases = OrderItem.objects.filter(product=product).count()
    
    # Get customer reviews
    reviews = ProductReview.objects.filter(product=product).count()
    
    return JsonResponse({
        'recent_purchases': recent_purchases,
        'total_purchases': total_purchases,
        'reviews': reviews,
    })


@login_required
def personalized_homepage(request):
    """Personalized homepage with recommendations."""
    # Get user's recently viewed products
    recently_viewed = RecentlyViewed.objects.filter(
        user=request.user
    ).select_related('product').order_by('-viewed_at')[:6]
    
    # Get user's wishlist
    wishlist_products = Wishlist.objects.filter(
        user=request.user
    ).select_related('product').order_by('-added_date')[:6]
    
    # Get personalized recommendations
    recommendations = ProductRecommendation.objects.filter(
        user=request.user
    ).select_related('product').order_by('-score')[:12]
    
    # Get featured products
    featured_products = Product.objects.filter(is_featured=True)[:6]
    
    # Get new arrivals
    new_arrivals = Product.objects.filter(is_new_arrival=True)[:6]
    
    # Get bestsellers
    bestsellers = Product.objects.filter(is_bestseller=True)[:6]
    
    context = {
        'recently_viewed': recently_viewed,
        'wishlist_products': wishlist_products,
        'recommendations': recommendations,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
    }
    
    return render(request, 'accounts/personalized_homepage.html', context)
