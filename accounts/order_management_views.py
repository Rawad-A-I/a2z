"""
Advanced order management and fulfillment views.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from datetime import datetime, timedelta

from .models import Order, OrderItem, OrderFulfillment, CustomerSupport
from products.models import Product, StockMovement


def is_staff_user(user):
    """Check if user is staff member."""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def order_management_dashboard(request):
    """Order management dashboard."""
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    processing_orders = Order.objects.filter(status='processing').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('user', 'assigned_employee').order_by('-order_date')[:10]
    
    # Orders requiring attention
    urgent_orders = Order.objects.filter(
        Q(status='pending') | Q(status='confirmed'),
        order_date__lte=timezone.now() - timedelta(hours=24)
    ).order_by('order_date')
    
    # Fulfillment statistics
    fulfillment_stats = {
        'pending': OrderFulfillment.objects.filter(status='pending').count(),
        'picked': OrderFulfillment.objects.filter(status='picked').count(),
        'packed': OrderFulfillment.objects.filter(status='packed').count(),
        'shipped': OrderFulfillment.objects.filter(status='shipped').count(),
        'delivered': OrderFulfillment.objects.filter(status='delivered').count(),
    }
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'recent_orders': recent_orders,
        'urgent_orders': urgent_orders,
        'fulfillment_stats': fulfillment_stats,
    }
    
    return render(request, 'accounts/order_management_dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def order_list(request):
    """List all orders with filtering."""
    orders = Order.objects.select_related('user', 'assigned_employee').order_by('-order_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by assigned employee
    employee_filter = request.GET.get('employee')
    if employee_filter:
        orders = orders.filter(assigned_employee_id=employee_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(order_date__date__gte=date_from)
    if date_to:
        orders = orders.filter(order_date__date__lte=date_to)
    
    # Search by order ID or customer
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 25)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    # Get employees for filter
    employees = User.objects.filter(is_staff=True)
    
    context = {
        'orders': orders_page,
        'employees': employees,
        'status_choices': Order._meta.get_field('status').choices,
    }
    
    return render(request, 'accounts/order_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def order_detail(request, order_id):
    """Detailed order view with fulfillment options."""
    order = get_object_or_404(Order, order_id=order_id)
    order_items = order.order_items.select_related('product', 'size_variant', 'color_variant')
    
    # Get or create fulfillment record
    fulfillment, created = OrderFulfillment.objects.get_or_create(order=order)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {new_status}.')
        
        elif action == 'assign_employee':
            employee_id = request.POST.get('employee')
            if employee_id:
                order.assigned_employee_id = employee_id
                order.save()
                messages.success(request, 'Order assigned to employee.')
        
        elif action == 'update_fulfillment':
            fulfillment_status = request.POST.get('fulfillment_status')
            tracking_number = request.POST.get('tracking_number')
            shipping_method = request.POST.get('shipping_method')
            carrier = request.POST.get('carrier')
            notes = request.POST.get('notes')
            
            fulfillment.status = fulfillment_status
            if tracking_number:
                fulfillment.tracking_number = tracking_number
            if shipping_method:
                fulfillment.shipping_method = shipping_method
            if carrier:
                fulfillment.carrier = carrier
            if notes:
                fulfillment.notes = notes
            fulfillment.save()
            
            messages.success(request, 'Fulfillment status updated.')
        
        elif action == 'add_notes':
            notes = request.POST.get('notes')
            order.notes = notes
            order.save()
            messages.success(request, 'Notes added to order.')
        
        return redirect('order_detail', order_id=order_id)
    
    # Get employees for assignment
    employees = User.objects.filter(is_staff=True)
    
    context = {
        'order': order,
        'order_items': order_items,
        'fulfillment': fulfillment,
        'employees': employees,
        'status_choices': Order._meta.get_field('status').choices,
        'fulfillment_choices': OrderFulfillment._meta.get_field('status').choices,
    }
    
    return render(request, 'accounts/order_detail.html', context)


@login_required
@user_passes_test(is_staff_user)
def fulfillment_center(request):
    """Fulfillment center for picking and packing."""
    # Orders ready for fulfillment
    ready_orders = Order.objects.filter(
        status__in=['confirmed', 'processing']
    ).select_related('user', 'assigned_employee').order_by('order_date')
    
    # Filter by fulfillment status
    fulfillment_status = request.GET.get('fulfillment_status')
    if fulfillment_status:
        ready_orders = ready_orders.filter(fulfillment__status=fulfillment_status)
    
    # Filter by assigned employee
    employee_filter = request.GET.get('employee')
    if employee_filter:
        ready_orders = ready_orders.filter(assigned_employee_id=employee_filter)
    
    context = {
        'orders': ready_orders,
        'employees': User.objects.filter(is_staff=True),
        'fulfillment_choices': OrderFulfillment._meta.get_field('status').choices,
    }
    
    return render(request, 'accounts/fulfillment_center.html', context)


@login_required
@user_passes_test(is_staff_user)
def pick_list(request, order_id):
    """Generate pick list for order fulfillment."""
    order = get_object_or_404(Order, order_id=order_id)
    order_items = order.order_items.select_related('product')
    
    # Group items by location (if you have warehouse locations)
    # For now, just show all items
    pick_items = []
    for item in order_items:
        pick_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'location': 'A-1-1',  # Default location
            'picked': False,
        })
    
    context = {
        'order': order,
        'pick_items': pick_items,
    }
    
    return render(request, 'accounts/pick_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_fulfillment_status(request, order_id):
    """Update fulfillment status via AJAX."""
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, order_id=order_id)
            fulfillment = order.fulfillment
            
            data = json.loads(request.body)
            new_status = data.get('status')
            tracking_number = data.get('tracking_number', '')
            carrier = data.get('carrier', '')
            
            fulfillment.status = new_status
            if tracking_number:
                fulfillment.tracking_number = tracking_number
            if carrier:
                fulfillment.carrier = carrier
            fulfillment.save()
            
            # Update order status based on fulfillment
            if new_status == 'shipped':
                order.status = 'shipped'
                order.save()
            elif new_status == 'delivered':
                order.status = 'delivered'
                order.save()
            
            return JsonResponse({
                'success': True,
                'status': fulfillment.status,
                'tracking_number': fulfillment.tracking_number,
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_staff_user)
def order_analytics(request):
    """Order analytics and reporting."""
    # Order volume over time
    order_volume = []
    for i in range(30):  # Last 30 days
        date = timezone.now().date() - timedelta(days=i)
        count = Order.objects.filter(order_date__date=date).count()
        order_volume.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Order status distribution
    status_distribution = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Average order value
    avg_order_value = Order.objects.aggregate(avg=Sum('grand_total'))['avg'] or 0
    total_orders = Order.objects.count()
    if total_orders > 0:
        avg_order_value = avg_order_value / total_orders
    
    # Top products by order count
    top_products = OrderItem.objects.values('product__product_name').annotate(
        total_quantity=Sum('quantity'),
        order_count=Count('order')
    ).order_by('-total_quantity')[:10]
    
    # Employee performance
    employee_performance = User.objects.filter(
        is_staff=True,
        assigned_orders__isnull=False
    ).annotate(
        orders_handled=Count('assigned_orders'),
        total_value=Sum('assigned_orders__grand_total')
    ).order_by('-orders_handled')
    
    context = {
        'order_volume': order_volume,
        'status_distribution': status_distribution,
        'avg_order_value': avg_order_value,
        'top_products': top_products,
        'employee_performance': employee_performance,
    }
    
    return render(request, 'accounts/order_analytics.html', context)


@login_required
@user_passes_test(is_staff_user)
def bulk_order_actions(request):
    """Bulk actions for multiple orders."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_ids = data.get('order_ids', [])
            action = data.get('action')
            
            orders = Order.objects.filter(order_id__in=order_ids)
            
            if action == 'assign_employee':
                employee_id = data.get('employee_id')
                orders.update(assigned_employee_id=employee_id)
                return JsonResponse({'success': True, 'message': 'Orders assigned to employee.'})
            
            elif action == 'update_status':
                new_status = data.get('status')
                orders.update(status=new_status)
                return JsonResponse({'success': True, 'message': f'Orders status updated to {new_status}.'})
            
            elif action == 'export':
                # Export orders to CSV
                import csv
                from django.http import HttpResponse
                
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="orders.csv"'
                
                writer = csv.writer(response)
                writer.writerow(['Order ID', 'Customer', 'Date', 'Status', 'Total'])
                
                for order in orders:
                    writer.writerow([
                        order.order_id,
                        order.user.get_full_name(),
                        order.order_date.strftime('%Y-%m-%d'),
                        order.status,
                        order.grand_total
                    ])
                
                return response
            
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_staff_user)
def order_returns(request):
    """Handle order returns and refunds."""
    # This would integrate with your return policy
    # For now, just show orders that might be eligible for return
    return_eligible_orders = Order.objects.filter(
        status='delivered',
        order_date__gte=timezone.now() - timedelta(days=30)  # 30-day return window
    ).select_related('user')
    
    context = {
        'return_eligible_orders': return_eligible_orders,
    }
    
    return render(request, 'accounts/order_returns.html', context)
