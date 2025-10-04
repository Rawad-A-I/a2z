"""
Modern Order Management Dashboard Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Q
from accounts.models import Order
from products.models import Product


@login_required
def modern_order_dashboard(request):
    """
    Modern order management dashboard with analytics and charts
    """
    # Get current date for display
    current_date = timezone.now()
    
    # Calculate date range for revenue chart (last 7 days)
    end_date = current_date
    start_date = end_date - timedelta(days=7)
    date_range = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}"
    
    # Order statistics
    total_orders = Order.objects.count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    processing_orders = Order.objects.filter(status='processing').count()
    
    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user').order_by('-order_date')[:10]
    
    # Prepare recent orders data for template
    recent_orders_data = []
    for order in recent_orders:
        # Get the first product from the order for display
        first_item = order.orderitem_set.first()
        product_name = first_item.product.name if first_item else "Product"
        
        recent_orders_data.append({
            'product_name': product_name,
            'customer_name': order.user.get_full_name() or order.user.username,
            'quantity': first_item.quantity if first_item else 1,
            'price': order.grand_total,
            'order_id': order.order_id,
        })
    
    # Order status distribution for chart
    status_counts = {
        'accepted': confirmed_orders,
        'rejected': cancelled_orders,
        'dispatched': processing_orders,
        'delivered': delivered_orders,
        'cancelled': cancelled_orders,
    }
    
    # Revenue data for chart (mock data for now - you can implement real revenue tracking)
    revenue_data = [2000, 2500, 1800, 3200, 2800, 3275, 3000, 3500]
    
    # Delivery tracking orders
    delivery_orders = Order.objects.filter(
        status__in=['processing', 'shipped', 'delivered']
    ).order_by('-order_date')[:2]
    
    context = {
        'current_date': current_date,
        'date_range': date_range,
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'processing_orders': processing_orders,
        'recent_orders': recent_orders_data,
        'status_counts': status_counts,
        'revenue_data': revenue_data,
        'delivery_orders': delivery_orders,
    }
    
    return render(request, 'accounts/modern_order_dashboard.html', context)
