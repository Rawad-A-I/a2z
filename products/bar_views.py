from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category
from accounts.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def bar_home(request):
    """Bar home page with featured products and categories"""
    # Get bar-specific products
    bar_products = Product.objects.filter(
        Q(section='bar') | Q(section='both')
    ).filter(is_in_stock=True)
    
    # Featured bar products
    featured_products = bar_products.filter(is_featured=True)[:8]
    
    # New arrivals for bar
    new_arrivals = bar_products.filter(is_new_arrival=True)[:6]
    
    # Bar categories
    bar_categories = Category.objects.filter(
        products__section__in=['bar', 'both']
    ).distinct()[:6]
    
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'bar_categories': bar_categories,
        'section': 'bar'
    }
    
    return render(request, 'products/bar_home.html', context)


def bar_products(request):
    """Bar products listing with filtering"""
    products = Product.objects.filter(
        Q(section='bar') | Q(section='both')
    ).filter(is_in_stock=True)
    
    # Category filtering
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Search filtering
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(product_desription__icontains=search_query) |
            Q(category__category_name__icontains=search_query)
        )
    
    # Price filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('product_name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Get categories for filter sidebar
    categories = Category.objects.filter(
        products__section__in=['bar', 'both']
    ).distinct()
    
    context = {
        'products': products_page,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'sort_by': sort_by,
        'section': 'bar',
        'show_search_bar': True,  # Show search bar on bar products page
    }
    
    return render(request, 'products/bar_products.html', context)


def bar_product_detail(request, slug):
    """Bar product detail page"""
    product = get_object_or_404(Product, slug=slug)
    
    # Check if product is available in bar section
    if product.section not in ['bar', 'both']:
        return render(request, 'products/product_not_available.html', {
            'section': 'bar',
            'message': 'This product is not available in the bar section.'
        })
    
    # Get related products from bar section
    related_products = Product.objects.filter(
        Q(section='bar') | Q(section='both')
    ).filter(
        category=product.category
    ).exclude(uid=product.uid)[:4]
    
    # Get product reviews
    reviews = product.reviews.all().order_by('-created_at')[:5]
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'section': 'bar'
    }
    
    return render(request, 'products/bar_product_detail.html', context)


@login_required
def add_to_bar_cart(request, product_id):
    """Add product to cart from bar section"""
    if request.method == 'POST':
        product = get_object_or_404(Product, uid=product_id)
        
        # Check if product is available in bar section
        if product.section not in ['bar', 'both']:
            return JsonResponse({
                'success': False,
                'message': 'This product is not available in the bar section.'
            })
        
        cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.product_name} added to cart!',
            'cart_count': cart.get_cart_count()
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def bar_categories(request):
    """Bar categories listing"""
    categories = Category.objects.filter(
        products__section__in=['bar', 'both']
    ).distinct()
    
    # Add product count for each category
    for category in categories:
        category.product_count = Product.objects.filter(
            category=category,
            section__in=['bar', 'both']
        ).count()
    
    context = {
        'categories': categories,
        'section': 'bar'
    }
    
    return render(request, 'products/bar_categories.html', context)
