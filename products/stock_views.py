"""
Stock and inventory management views.
"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import models
from .models import Product
import json


def is_staff_user(user):
    """Check if user is staff member."""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def stock_dashboard(request):
    """Stock management dashboard."""
    products = Product.objects.all().order_by('-created_at')
    
    # Filter options
    low_stock = request.GET.get('low_stock')
    out_of_stock = request.GET.get('out_of_stock')
    
    if low_stock:
        products = products.filter(stock_quantity__lte=models.F('low_stock_threshold'))
    if out_of_stock:
        products = products.filter(is_in_stock=False)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'total_products': Product.objects.count(),
        'low_stock_products': Product.objects.filter(
            stock_quantity__lte=models.F('low_stock_threshold')
        ).count(),
        'out_of_stock_products': Product.objects.filter(is_in_stock=False).count(),
    }
    
    return render(request, 'products/stock_dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_stock(request, product_id):
    """Update stock quantity for a product."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 0))
            action = data.get('action', 'set')  # 'set', 'add', 'subtract'
            
            if action == 'set':
                product.stock_quantity = quantity
            elif action == 'add':
                product.stock_quantity += quantity
            elif action == 'subtract':
                product.stock_quantity = max(0, product.stock_quantity - quantity)
            
            product.is_in_stock = product.stock_quantity > 0
            product.save()
            
            return JsonResponse({
                'success': True,
                'new_quantity': product.stock_quantity,
                'is_in_stock': product.is_in_stock,
                'is_low_stock': product.is_low_stock()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_staff_user)
def bulk_stock_update(request):
    """Bulk update stock for multiple products."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            updates = data.get('updates', [])
            
            updated_products = []
            for update in updates:
                product = get_object_or_404(Product, id=update['product_id'])
                quantity = int(update['quantity'])
                action = update.get('action', 'set')
                
                if action == 'set':
                    product.stock_quantity = quantity
                elif action == 'add':
                    product.stock_quantity += quantity
                elif action == 'subtract':
                    product.stock_quantity = max(0, product.stock_quantity - quantity)
                
                product.is_in_stock = product.stock_quantity > 0
                product.save()
                
                updated_products.append({
                    'id': product.id,
                    'name': product.product_name,
                    'quantity': product.stock_quantity,
                    'is_in_stock': product.is_in_stock
                })
            
            return JsonResponse({
                'success': True,
                'updated_products': updated_products
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_staff_user)
def stock_alerts(request):
    """View stock alerts and notifications."""
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=models.F('low_stock_threshold')
    ).filter(is_in_stock=True)
    
    out_of_stock_products = Product.objects.filter(is_in_stock=False)
    
    context = {
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
    }
    
    return render(request, 'products/stock_alerts.html', context)


@login_required
def check_stock_availability(request, product_id):
    """Check if product is available in stock."""
    try:
        product = get_object_or_404(Product, id=product_id)
        requested_quantity = int(request.GET.get('quantity', 1))
        
        available = product.can_fulfill_order(requested_quantity)
        
        return JsonResponse({
            'available': available,
            'stock_quantity': product.stock_quantity,
            'is_in_stock': product.is_in_stock,
            'is_low_stock': product.is_low_stock()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
