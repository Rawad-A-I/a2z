from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, F, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Product, Barcode, Category, ProductImage
from .forms import BarcodeForm, ProductInsertionForm, BulkBarcodeForm, ProductImageForm
from accounts.models import Order, OrderItem


def is_employee(user):
    """Check if user is an employee"""
    return user.is_staff


@login_required
def employee_product_management(request):
    """Enhanced employee product management dashboard with admin-like features"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access. Please log in with staff credentials.')
        return redirect('login')
    
    # Get all products with related data
    products = Product.objects.select_related('category').prefetch_related('product_images', 'variants')
    
    # Advanced filtering
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(product_desription__icontains=search_query) |
            Q(category__category_name__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Stock filter with enhanced options
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        products = products.filter(stock_quantity__lte=F('low_stock_threshold'))
    elif stock_filter == 'out':
        products = products.filter(stock_quantity=0)
    elif stock_filter == 'in':
        products = products.filter(stock_quantity__gt=0)
    elif stock_filter == 'newest':
        products = products.filter(newest_product=True)
    
    # Price range filter
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    
    # Sorting options
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['product_name', '-product_name', 'price', '-price', 'stock_quantity', '-stock_quantity', 'created_at', '-created_at']
    if sort_by in valid_sorts:
        products = products.order_by(sort_by)
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = Category.objects.all()
    
    # Calculate statistics for dashboard
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock_quantity__lte=F('low_stock_threshold')).count()
    out_of_stock_count = Product.objects.filter(stock_quantity=0).count()
    newest_products_count = Product.objects.filter(newest_product=True).count()
    
    # Get recent products for quick access
    recent_products = Product.objects.select_related('category').order_by('-created_at')[:5]
    
    context = {
        'products': products_page,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'sort_by': sort_by,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'newest_products_count': newest_products_count,
        'recent_products': recent_products,
    }
    return render(request, 'products/employee_product_management.html', context)


@login_required
def bulk_product_actions(request):
    """Bulk actions for products - Employee only"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            messages.warning(request, 'Please select products to perform bulk actions.')
            return redirect('employee_product_management')
        
        products = Product.objects.filter(uid__in=product_ids)
        
        if action == 'update_stock':
            stock_value = request.POST.get('stock_value')
            if stock_value:
                products.update(stock_quantity=int(stock_value))
                messages.success(request, f'Updated stock for {len(products)} products.')
        
        elif action == 'update_price':
            price_value = request.POST.get('price_value')
            if price_value:
                products.update(price=int(price_value))
                messages.success(request, f'Updated price for {len(products)} products.')
        
        elif action == 'toggle_newest':
            for product in products:
                product.newest_product = not product.newest_product
                product.save()
            messages.success(request, f'Toggled newest status for {len(products)} products.')
        
        elif action == 'delete':
            count = products.count()
            products.delete()
            messages.success(request, f'Deleted {count} products.')
        
        return redirect('employee_product_management')
    
    return redirect('employee_product_management')


@login_required
def quick_edit_product(request, product_id):
    """Quick edit product - Employee only"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    product = get_object_or_404(Product, uid=product_id)
    
    if request.method == 'POST':
        # Quick update of all fields
        product.product_name = request.POST.get('product_name', product.product_name)
        product.price = int(request.POST.get('price', product.price))
        product.stock_quantity = int(request.POST.get('stock_quantity', product.stock_quantity))
        product.low_stock_threshold = int(request.POST.get('low_stock_threshold', product.low_stock_threshold))
        product.is_in_stock = request.POST.get('is_in_stock') == 'on'
        product.newest_product = request.POST.get('newest_product') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_bestseller = request.POST.get('is_bestseller') == 'on'
        product.is_new_arrival = request.POST.get('is_new_arrival') == 'on'
        
        # Physical properties
        weight = request.POST.get('weight')
        if weight:
            product.weight = float(weight)
        product.dimensions = request.POST.get('dimensions', product.dimensions)
        
        # Section
        product.section = request.POST.get('section', product.section)
        
        # SEO fields
        product.meta_title = request.POST.get('meta_title', product.meta_title)
        product.meta_description = request.POST.get('meta_description', product.meta_description)
        product.keywords = request.POST.get('keywords', product.keywords)
        
        # Description
        product.product_desription = request.POST.get('product_desription', product.product_desription)
        
        product.save()
        messages.success(request, f'Product "{product.product_name}" updated successfully.')
        return redirect('employee_product_management')
    
    return render(request, 'products/quick_edit_product.html', {'product': product})


@login_required
def product_analytics(request):
    """Product analytics dashboard - Employee only"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    # Time periods
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    # Product performance metrics
    top_selling_products = Product.objects.annotate(
        total_sold=Sum('order_items__quantity', filter=Q(order_items__order__order_date__gte=last_30_days))
    ).filter(total_sold__gt=0).order_by('-total_sold')[:10]
    
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).order_by('stock_quantity')[:10]
    
    # Category performance
    category_stats = Category.objects.annotate(
        product_count=Count('product'),
        total_sales=Sum('product__order_items__quantity', filter=Q(product__order_items__order__order_date__gte=last_30_days))
    ).order_by('-total_sales')
    
    # Recent activity
    recent_orders = Order.objects.filter(
        order_date__gte=last_7_days
    ).select_related('user').order_by('-order_date')[:10]
    
    # Stock alerts
    out_of_stock = Product.objects.filter(stock_quantity=0).count()
    low_stock = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold'),
        stock_quantity__gt=0
    ).count()
    
    context = {
        'top_selling_products': top_selling_products,
        'low_stock_products': low_stock_products,
        'category_stats': category_stats,
        'recent_orders': recent_orders,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'last_30_days': last_30_days,
        'last_7_days': last_7_days,
    }
    
    return render(request, 'products/product_analytics.html', context)


@login_required
def add_product(request):
    """Add new product - Employee only"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    if request.method == 'POST':
        form = ProductInsertionForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Handle product images
            product_images = request.FILES.getlist('product_images')
            if product_images:
                for i, image in enumerate(product_images):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        alt_text=f"{product.product_name} - Image {i+1}",
                        is_primary=(i == 0),  # First image is primary
                        sort_order=i
                    )
                messages.success(request, f'Product "{product.product_name}" created with {len(product_images)} image(s)')
            
            # Handle barcode creation
            barcode_value = request.POST.get('barcode_value', '').strip()
            barcode_type = request.POST.get('barcode_type', 'GENERATED')
            is_primary = request.POST.get('is_primary') == 'on'
            is_active = request.POST.get('is_active') == 'on'
            barcode_notes = request.POST.get('barcode_notes', '')
            
            # Create barcode if provided or generate one
            if barcode_value:
                # Check if barcode already exists
                if Barcode.objects.filter(barcode_value=barcode_value).exists():
                    messages.error(request, f'Barcode {barcode_value} already exists. Please use a different barcode.')
                    context = {
                        'form': form,
                        'categories': Category.objects.all(),
                    }
                    return render(request, 'products/add_product.html', context)
                
                Barcode.objects.create(
                    product=product,
                    barcode_value=barcode_value,
                    barcode_type=barcode_type,
                    is_primary=is_primary,
                    is_active=is_active,
                    notes=barcode_notes
                )
                messages.success(request, f'Product "{product.product_name}" created with barcode: {barcode_value}')
            else:
                # Auto-generate barcode
                barcode_value = Barcode.generate_barcode()
                Barcode.objects.create(
                    product=product,
                    barcode_value=barcode_value,
                    barcode_type='GENERATED',
                    is_primary=True,
                    is_active=True,
                    notes='Auto-generated barcode'
                )
                messages.success(request, f'Product "{product.product_name}" created with auto-generated barcode: {barcode_value}')
            
            return redirect('employee_product_management')
    else:
        form = ProductInsertionForm()
    
    context = {
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'products/add_product.html', context)


@login_required
def product_barcode_management(request, product_id):
    """Manage barcodes for a specific product"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    product = get_object_or_404(Product, uid=product_id)
    barcodes = product.barcodes.all()
    
    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            barcode = form.save(commit=False)
            barcode.product = product
            
            # Check if barcode already exists
            if Barcode.objects.filter(barcode_value=barcode.barcode_value).exists():
                messages.error(request, 'This barcode already exists for another product.')
            else:
                barcode.save()
                messages.success(request, f'Barcode {barcode.barcode_value} added to {product.product_name}.')
                return redirect('product_barcode_management', product_id=product_id)
    else:
        form = BarcodeForm()
    
    context = {
        'product': product,
        'barcodes': barcodes,
        'form': form,
    }
    return render(request, 'products/product_barcode_management.html', context)


@login_required
def bulk_barcode_upload(request):
    """Bulk upload barcodes"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    if request.method == 'POST':
        form = BulkBarcodeForm(request.POST)
        if form.is_valid():
            barcode_data = form.cleaned_data['barcode_data']
            success_count = 0
            error_count = 0
            
            for item in barcode_data:
                try:
                    # Find product by name
                    product = Product.objects.get(product_name__iexact=item['product_name'])
                    
                    # Create barcode
                    Barcode.objects.create(
                        product=product,
                        barcode_value=item['barcode_value'],
                        barcode_type=item['barcode_type'],
                        notes='Bulk uploaded'
                    )
                    success_count += 1
                except Product.DoesNotExist:
                    error_count += 1
                except Exception as e:
                    error_count += 1
            
            messages.success(request, f'Bulk upload completed: {success_count} successful, {error_count} errors.')
            return redirect('employee_product_management')
    else:
        form = BulkBarcodeForm()
    
    context = {
        'form': form,
    }
    return render(request, 'products/bulk_barcode_upload.html', context)


@login_required
def barcode_search(request):
    """Search products by barcode"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    barcode_value = request.GET.get('barcode', '')
    product = None
    barcode = None
    
    if barcode_value:
        try:
            barcode = Barcode.objects.get(barcode_value=barcode_value, is_active=True)
            product = barcode.product
        except Barcode.DoesNotExist:
            messages.warning(request, f'No product found with barcode: {barcode_value}')
    
    context = {
        'barcode_value': barcode_value,
        'product': product,
        'barcode': barcode,
    }
    return render(request, 'products/barcode_search.html', context)


@login_required
def delete_barcode(request, barcode_id):
    """Delete a barcode"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    barcode = get_object_or_404(Barcode, uid=barcode_id)
    product = barcode.product
    
    if request.method == 'POST':
        barcode_value = barcode.barcode_value
        barcode.delete()
        messages.success(request, f'Barcode {barcode_value} deleted from {product.product_name}.')
        return redirect('product_barcode_management', product_id=product.uid)
    
    context = {
        'barcode': barcode,
        'product': product,
    }
    return render(request, 'products/delete_barcode.html', context)
