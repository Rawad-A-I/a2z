from django.db.models import Q
from django.shortcuts import render
from products.models import Product, Category
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.


def redirect_homepage(request):
    """Redirect homepage with 3 platform options"""
    return render(request, 'home/redirect_homepage.html')


def index(request):
    """A2Z Mart - Main e-commerce site"""
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

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_sort': selected_sort,
    }
    return render(request, 'home/index.html', context)


def product_search(request):
    query = request.GET.get('q', '')

    if query:
        # Search for products that contain the query string in their product_name field
        products = Product.objects.filter(Q(product_name__icontains=query) | Q(
            product_name__istartswith=query))
    else:
        products = Product.objects.none()

    context = {'query': query, 'products': products}
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


def a2z_bar(request):
    """A2Z Bar - Coming soon page"""
    return render(request, 'home/a2z_bar.html')


def rayan_brayan(request):
    """Rayan O Brayan - Coming soon page"""
    return render(request, 'home/rayan_brayan.html')
