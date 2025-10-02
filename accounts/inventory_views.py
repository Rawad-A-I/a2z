"""
Advanced inventory management views.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import InventoryAlert, StoreLocation
from products.models import Product, ProductVariant, StockMovement


def is_staff_user(user):
    """Check if user is staff member."""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def inventory_dashboard(request):
    """Main inventory dashboard."""
    # Get inventory statistics
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).count()
    out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
    total_stock_value = sum(product.price * product.stock_quantity for product in Product.objects.all())
    
    # Recent stock movements
    recent_movements = StockMovement.objects.select_related('product', 'user').order_by('-created_at')[:10]
    
    # Low stock alerts
    low_stock_alerts = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).order_by('stock_quantity')[:10]
    
    # Store locations
    store_locations = StoreLocation.objects.filter(is_active=True)
    
    context = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_stock_value': total_stock_value,
        'recent_movements': recent_movements,
        'low_stock_alerts': low_stock_alerts,
        'store_locations': store_locations,
    }
    
    return render(request, 'accounts/inventory_dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def stock_movements(request):
    """View stock movements with filtering."""
    movements = StockMovement.objects.select_related('product', 'user').order_by('-created_at')
    
    # Filter by product
    product_id = request.GET.get('product')
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    # Filter by movement type
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        movements = movements.filter(created_at__date__gte=date_from)
    if date_to:
        movements = movements.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(movements, 25)
    page_number = request.GET.get('page')
    movements_page = paginator.get_page(page_number)
    
    # Get products for filter dropdown
    products = Product.objects.all().order_by('product_name')
    
    context = {
        'movements': movements_page,
        'products': products,
        'movement_types': StockMovement._meta.get_field('movement_type').choices,
    }
    
    return render(request, 'accounts/stock_movements.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_stock(request, product_id):
    """Update product stock."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, uid=product_id)
            data = json.loads(request.body)
            
            movement_type = data.get('movement_type')
            quantity = int(data.get('quantity', 0))
            reason = data.get('reason', '')
            reference = data.get('reference', '')
            
            if movement_type == 'in':
                product.stock_quantity += quantity
            elif movement_type == 'out':
                if product.stock_quantity < quantity:
                    return JsonResponse({'error': 'Insufficient stock'}, status=400)
                product.stock_quantity -= quantity
            elif movement_type == 'adjustment':
                product.stock_quantity = quantity
            
            product.is_in_stock = product.stock_quantity > 0
            product.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                reason=reason,
                reference=reference,
                user=request.user
            )
            
            return JsonResponse({
                'success': True,
                'new_stock': product.stock_quantity,
                'is_in_stock': product.is_in_stock
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
            
            results = []
            for update in updates:
                product = get_object_or_404(Product, uid=update['product_id'])
                movement_type = update.get('movement_type')
                quantity = int(update.get('quantity', 0))
                reason = update.get('reason', 'Bulk update')
                
                if movement_type == 'in':
                    product.stock_quantity += quantity
                elif movement_type == 'out':
                    if product.stock_quantity < quantity:
                        results.append({
                            'product_id': str(product.uid),
                            'error': 'Insufficient stock'
                        })
                        continue
                    product.stock_quantity -= quantity
                elif movement_type == 'adjustment':
                    product.stock_quantity = quantity
                
                product.is_in_stock = product.stock_quantity > 0
                product.save()
                
                # Create stock movement record
                StockMovement.objects.create(
                    product=product,
                    movement_type=movement_type,
                    quantity=quantity,
                    reason=reason,
                    user=request.user
                )
                
                results.append({
                    'product_id': str(product.uid),
                    'success': True,
                    'new_stock': product.stock_quantity
                })
            
            return JsonResponse({'results': results})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_staff_user)
def stock_alerts(request):
    """View and manage stock alerts."""
    alerts = InventoryAlert.objects.select_related('product').filter(is_active=True)
    
    # Filter by alert status
    alert_status = request.GET.get('status')
    if alert_status == 'triggered':
        alerts = alerts.filter(alert_sent=True)
    elif alert_status == 'pending':
        alerts = alerts.filter(alert_sent=False)
    
    # Check for new alerts
    for alert in alerts:
        alert.check_alert()
    
    context = {
        'alerts': alerts,
    }
    
    return render(request, 'accounts/stock_alerts.html', context)


@login_required
@user_passes_test(is_staff_user)
def inventory_reports(request):
    """Generate inventory reports."""
    report_type = request.GET.get('type', 'stock_levels')
    
    if report_type == 'stock_levels':
        products = Product.objects.all().order_by('stock_quantity')
        context = {
            'products': products,
            'report_type': 'stock_levels',
        }
    elif report_type == 'movements':
        movements = StockMovement.objects.select_related('product').order_by('-created_at')
        context = {
            'movements': movements,
            'report_type': 'movements',
        }
    elif report_type == 'low_stock':
        products = Product.objects.filter(
            stock_quantity__lte=F('low_stock_threshold')
        ).order_by('stock_quantity')
        context = {
            'products': products,
            'report_type': 'low_stock',
        }
    else:
        context = {'report_type': 'overview'}
    
    return render(request, 'accounts/inventory_reports.html', context)


@login_required
@user_passes_test(is_staff_user)
def store_locations(request):
    """Manage store locations."""
    locations = StoreLocation.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        StoreLocation.objects.create(
            name=name,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
            email=email
        )
        messages.success(request, 'Store location added successfully.')
        return redirect('store_locations')
    
    context = {
        'locations': locations,
    }
    
    return render(request, 'accounts/store_locations.html', context)


@login_required
@user_passes_test(is_staff_user)
def edit_store_location(request, location_id):
    """Edit store location."""
    location = get_object_or_404(StoreLocation, uid=location_id)
    
    if request.method == 'POST':
        location.name = request.POST.get('name')
        location.address = request.POST.get('address')
        location.city = request.POST.get('city')
        location.state = request.POST.get('state')
        location.zip_code = request.POST.get('zip_code')
        location.phone = request.POST.get('phone')
        location.email = request.POST.get('email')
        location.save()
        
        messages.success(request, 'Store location updated successfully.')
        return redirect('store_locations')
    
    context = {
        'location': location,
    }
    
    return render(request, 'accounts/edit_store_location.html', context)
