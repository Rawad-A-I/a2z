from django.db.models import Q
from django.shortcuts import render
from products.models import Product, Category
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django_user_agents.utils import get_user_agent

# Create your views here.

def redirect_homepage(request):
    """Redirect homepage with 3 platform options"""
    return render(request, 'home/redirect_homepage.html')


def index(request):
    """A2Z Mart - Main e-commerce site with hero section"""
    query = Product.objects.all().order_by('uid')  # Use 'uid' instead of 'id'
    categories = Category.objects.all()
    selected_sort = request.GET.get('sort')
    selected_category = request.GET.get('category')

    if selected_category:
        query = query.filter(category__category_name=selected_category)

    if selected_sort:
        if selected_sort == 'newest':
            query = query.filter(newest_product=True).order_by('category_id')
        elif selected_sort == 'priceAsc':
            query = query.order_by('price')
        elif selected_sort == 'priceDesc':
            query = query.order_by('-price')
    else:
        # Ensure there's always an ordering
        query = query.order_by('uid')

    page = request.GET.get('page', 1)
    paginator = Paginator(query, 20)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    except Exception as e:
        print(e)
        # Fallback to empty page if there's an error
        products = paginator.page(1)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_sort': selected_sort,
        'show_search_bar': False,  # Hide search bar on home page
    }
    
    # Detect mobile devices and serve optimized template
    if hasattr(request, 'is_mobile') and request.is_mobile:
        return render(request, 'home/mobile_index.html', context)
    
    return render(request, 'home/index.html', context)


def products_only(request):
    """A2Z Mart - Products only view without hero section"""
    query = Product.objects.all().order_by('uid')
    categories = Category.objects.all()
    selected_sort = request.GET.get('sort')
    selected_category = request.GET.get('category')

    if selected_category:
        query = query.filter(category__category_name=selected_category)

    if selected_sort:
        if selected_sort == 'newest':
            query = query.filter(newest_product=True).order_by('category_id')
        elif selected_sort == 'priceAsc':
            query = query.order_by('price')
        elif selected_sort == 'priceDesc':
            query = query.order_by('-price')
    else:
        query = query.order_by('uid')

    page = request.GET.get('page', 1)
    paginator = Paginator(query, 20)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    except Exception as e:
        print(e)
        products = paginator.page(1)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_sort': selected_sort,
        'show_search_bar': True,  # Show search bar on product pages
    }
    
    # Detect mobile devices and serve optimized template
    if hasattr(request, 'is_mobile') and request.is_mobile:
        return render(request, 'home/mobile_index.html', context)
    
    return render(request, 'home/products_only.html', context)


def product_search(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '')

    if query:
        # Enhanced search - search in multiple fields
        products = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(product_desription__icontains=query) |
            Q(category__category_name__icontains=query) |
            Q(keywords__icontains=query)
        ).distinct()
        
        # Apply category filter if provided
        if category_filter:
            products = products.filter(category__category_name=category_filter)
            
        # Apply sorting
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('product_name')
        elif sort_by == 'name_desc':
            products = products.order_by('-product_name')
        elif sort_by == 'newest':
            products = products.filter(newest_product=True).order_by('-created_at')
        else:
            # Default: relevance (products with query in name first)
            products = products.extra(
                select={
                    'relevance': "CASE WHEN product_name ILIKE %s THEN 1 ELSE 2 END"
                },
                select_params=[f'%{query}%']
            ).order_by('relevance', 'product_name')
    else:
        products = Product.objects.none()

    # Get categories for filter dropdown
    categories = Category.objects.all().order_by('category_name')

    context = {
        'query': query,
        'products': products,
        'categories': categories,
        'selected_category': category_filter,
        'selected_sort': sort_by,
        'show_search_bar': True,  # Show search bar on search results page
    }
    return render(request, 'home/search.html', context)


def contact(request):
    context = {"form_id": "xgvvlrvn"}
    return render(request, 'home/contact.html', context)


def about(request):
    return render(request, 'home/about.html')


def terms_and_conditions(request):
    return render(request, 'home/terms_and_conditions.html')


def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')


def demo_design_system(request):
    """Demo page showcasing the new design system"""
    return render(request, 'demo_design_system.html')


def a2z_bar(request):
    """A2Z Bar - Coming soon page"""
    return render(request, 'home/a2z_bar.html')


def rayan_brayan(request):
    """Rayan O Brayan - Coming soon page"""
    return render(request, 'home/rayan_brayan.html')
