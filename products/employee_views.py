from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Barcode, Category
from .forms import BarcodeForm, ProductInsertionForm, BulkBarcodeForm
from accounts.models import Order


def is_employee(user):
    """Check if user is an employee"""
    return user.is_staff


@login_required
def employee_product_management(request):
    """Employee product management dashboard"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    # Get products with pagination
    products = Product.objects.all().order_by('-created_at')
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products_page = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(product_description__icontains=search_query)
        ).order_by('-created_at')
        paginator = Paginator(products_page, 20)
        products_page = paginator.get_page(page_number)
    
    context = {
        'products': products_page,
        'search_query': search_query,
    }
    return render(request, 'products/employee_product_management.html', context)


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
            
            # Generate barcode if none provided
            if not product.barcodes.exists():
                barcode_value = Barcode.generate_barcode()
                Barcode.objects.create(
                    product=product,
                    barcode_value=barcode_value,
                    barcode_type='GENERATED',
                    is_primary=True,
                    notes='Auto-generated barcode'
                )
                messages.success(request, f'Product "{product.product_name}" created with auto-generated barcode: {barcode_value}')
            else:
                messages.success(request, f'Product "{product.product_name}" created successfully.')
            
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
