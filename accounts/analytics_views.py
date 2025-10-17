"""
Analytics and reporting views.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from datetime import datetime, timedelta

from .models import Order, OrderItem, CustomerLoyalty, Analytics, StoreLocation
from products.models import Product, ProductReview, StockMovement
from django.contrib.auth.models import User


def is_staff_user(user):
    """Check if user is staff member."""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def analytics_dashboard(request):
    """Main analytics dashboard."""
    # Sales analytics
    total_sales = Order.objects.aggregate(total=Sum('grand_total'))['total'] or 0
    total_orders = Order.objects.count()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Sales over time (last 30 days)
    sales_over_time = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        daily_sales = Order.objects.filter(
            order_date__date=date
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        sales_over_time.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
    
    # Top products
    top_products = OrderItem.objects.values(
        'product__product_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('product_price')
    ).order_by('-total_quantity')[:10]
    
    # Customer analytics
    total_customers = User.objects.filter(is_staff=False).count()
    new_customers_this_month = User.objects.filter(
        date_joined__gte=timezone.now().replace(day=1),
        is_staff=False
    ).count()
    
    # Order status distribution
    order_status_dist = Order.objects.values('status').annotate(
        count=Count('uid')
    ).order_by('-count')
    
    # Revenue by month
    revenue_by_month = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        monthly_revenue = Order.objects.filter(
            order_date__gte=month_start,
            order_date__lt=month_end
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        revenue_by_month.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(monthly_revenue)
        })
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'sales_over_time': sales_over_time,
        'top_products': top_products,
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'order_status_dist': order_status_dist,
        'revenue_by_month': revenue_by_month,
    }
    
    return render(request, 'accounts/analytics_dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def sales_analytics(request):
    """Detailed sales analytics."""
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from and date_to:
        orders = Order.objects.filter(
            order_date__date__gte=date_from,
            order_date__date__lte=date_to
        )
    else:
        # Default to last 30 days
        orders = Order.objects.filter(
            order_date__gte=timezone.now() - timedelta(days=30)
        )
    
    # Sales metrics
    total_revenue = orders.aggregate(total=Sum('grand_total'))['total'] or 0
    total_orders = orders.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Sales by day
    sales_by_day = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        daily_sales = orders.filter(order_date__date=date).aggregate(
            total=Sum('grand_total')
        )['total'] or 0
        daily_orders = orders.filter(order_date__date=date).count()
        sales_by_day.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(daily_sales),
            'orders': daily_orders
        })
    
    # Top performing products
    top_products = OrderItem.objects.filter(
        order__in=orders
    ).values(
        'product__product_name',
        'product__category__category_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('product_price')
    ).order_by('-total_revenue')[:20]
    
    # Sales by category
    sales_by_category = OrderItem.objects.filter(
        order__in=orders
    ).values(
        'product__category__category_name'
    ).annotate(
        total_revenue=Sum('product_price'),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'sales_by_day': sales_by_day,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'accounts/sales_analytics.html', context)


@login_required
@user_passes_test(is_staff_user)
def customer_analytics(request):
    """Customer analytics and insights."""
    # Customer acquisition over time
    customer_acquisition = []
    for i in range(12):  # Last 12 months
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        new_customers = User.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end,
            is_staff=False
        ).count()
        customer_acquisition.append({
            'month': month_start.strftime('%Y-%m'),
            'customers': new_customers
        })
    
    # Customer lifetime value
    customer_lifetime_value = CustomerLoyalty.objects.aggregate(
        avg_spent=Avg('total_spent')
    )['avg_spent'] or 0
    
    # Customer retention
    total_customers = User.objects.filter(is_staff=False).count()
    repeat_customers = User.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=1, is_staff=False).count()
    retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    # Customer segments
    customer_segments = CustomerLoyalty.objects.values('tier').annotate(
        count=Count('uid'),
        avg_spent=Avg('total_spent')
    ).order_by('-avg_spent')
    
    # Top customers
    top_customers = CustomerLoyalty.objects.order_by('-total_spent')[:20]
    
    # Customer behavior
    customer_behavior = {
        'avg_orders_per_customer': User.objects.annotate(
            order_count=Count('orders')
        ).filter(is_staff=False).aggregate(
            avg=Avg('order_count')
        )['avg'] or 0,
        'avg_reviews_per_customer': User.objects.annotate(
            review_count=Count('reviews')
        ).filter(is_staff=False).aggregate(
            avg=Avg('review_count')
        )['avg'] or 0,
    }
    
    context = {
        'customer_acquisition': customer_acquisition,
        'customer_lifetime_value': customer_lifetime_value,
        'retention_rate': retention_rate,
        'customer_segments': customer_segments,
        'top_customers': top_customers,
        'customer_behavior': customer_behavior,
    }
    
    return render(request, 'accounts/customer_analytics.html', context)


@login_required
@user_passes_test(is_staff_user)
def product_analytics(request):
    """Product performance analytics."""
    # Top selling products
    top_products = OrderItem.objects.values(
        'product__product_name',
        'product__category__category_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('product_price'),
        order_count=Count('order')
    ).order_by('-total_quantity')[:20]
    
    # Product categories performance
    category_performance = OrderItem.objects.values(
        'product__category__category_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('product_price'),
        product_count=Count('product', distinct=True)
    ).order_by('-total_revenue')
    
    # Product reviews analytics
    review_analytics = ProductReview.objects.values(
        'product__product_name'
    ).annotate(
        review_count=Count('uid'),
        avg_rating=Avg('stars')
    ).order_by('-review_count')[:20]
    
    # Stock analytics
    stock_analytics = Product.objects.annotate(
        total_movements=Count('stock_movements')
    ).filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).order_by('stock_quantity')
    
    # Product profitability (if you have cost data)
    # This would require adding cost fields to your Product model
    
    context = {
        'top_products': top_products,
        'category_performance': category_performance,
        'review_analytics': review_analytics,
        'stock_analytics': stock_analytics,
    }
    
    return render(request, 'accounts/product_analytics.html', context)


@login_required
@user_passes_test(is_staff_user)
def inventory_analytics(request):
    """Inventory analytics and insights."""
    # Stock levels
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).count()
    out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
    
    # Stock movements over time
    stock_movements = StockMovement.objects.values('created_at__date').annotate(
        total_in=Sum('quantity', filter=Q(movement_type='in')),
        total_out=Sum('quantity', filter=Q(movement_type='out'))
    ).order_by('-created_at__date')[:30]
    
    # Top moving products
    top_moving_products = StockMovement.objects.values(
        'product__product_name'
    ).annotate(
        total_movements=Sum('quantity')
    ).order_by('-total_movements')[:20]
    
    # Inventory value
    total_inventory_value = sum(
        product.price * product.stock_quantity 
        for product in Product.objects.all()
    )
    
    # Stock turnover (simplified calculation)
    stock_turnover = {}
    for product in Product.objects.all():
        total_sold = OrderItem.objects.filter(
            product=product
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        if product.stock_quantity > 0:
            turnover = total_sold / product.stock_quantity
            stock_turnover[product.product_name] = turnover
    
    context = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'stock_movements': stock_movements,
        'top_moving_products': top_moving_products,
        'total_inventory_value': total_inventory_value,
        'stock_turnover': stock_turnover,
    }
    
    return render(request, 'accounts/inventory_analytics.html', context)


@login_required
@user_passes_test(is_staff_user)
def export_analytics(request):
    """Export analytics data to CSV."""
    report_type = request.GET.get('type', 'sales')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
    
    writer = csv.writer(response)
    
    if report_type == 'sales':
        writer.writerow(['Date', 'Orders', 'Revenue', 'Avg Order Value'])
        
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            orders = Order.objects.filter(order_date__date=date)
            revenue = orders.aggregate(total=Sum('grand_total'))['total'] or 0
            order_count = orders.count()
            avg_order_value = revenue / order_count if order_count > 0 else 0
            
            writer.writerow([
                date.strftime('%Y-%m-%d'),
                order_count,
                revenue,
                avg_order_value
            ])
    
    elif report_type == 'products':
        writer.writerow(['Product', 'Category', 'Quantity Sold', 'Revenue'])
        
        products = OrderItem.objects.values(
            'product__product_name',
            'product__category__category_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('product_price')
        ).order_by('-total_quantity')
        
        for product in products:
            writer.writerow([
                product['product__product_name'],
                product['product__category__category_name'],
                product['total_quantity'],
                product['total_revenue']
            ])
    
    elif report_type == 'customers':
        writer.writerow(['Customer', 'Email', 'Total Spent', 'Orders', 'Tier'])
        
        customers = CustomerLoyalty.objects.select_related('user').order_by('-total_spent')
        
        for customer in customers:
            writer.writerow([
                customer.user.get_full_name(),
                customer.user.email,
                customer.total_spent,
                customer.user.orders.count(),
                customer.tier
            ])
    
    return response


@login_required
@user_passes_test(is_staff_user)
def custom_report(request):
    """Create custom reports."""
    if request.method == 'POST':
        report_name = request.POST.get('report_name')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        metrics = request.POST.getlist('metrics')
        
        # Generate custom report based on selected metrics
        # This is a simplified example
        report_data = {
            'name': report_name,
            'date_from': date_from,
            'date_to': date_to,
            'metrics': metrics,
            'generated_at': timezone.now(),
        }
        
        # Save report configuration
        # You can implement report saving functionality here
        
        messages.success(request, f'Custom report "{report_name}" generated successfully.')
        return redirect('analytics_dashboard')
    
    context = {
        'available_metrics': [
            'sales_revenue',
            'order_count',
            'customer_count',
            'product_performance',
            'inventory_levels',
            'customer_retention',
        ]
    }
    
    return render(request, 'accounts/custom_report.html', context)


@login_required
@user_passes_test(is_staff_user)
def real_time_analytics(request):
    """Real-time analytics dashboard."""
    # Get real-time data
    today = timezone.now().date()
    
    # Today's metrics
    today_orders = Order.objects.filter(order_date__date=today)
    today_revenue = today_orders.aggregate(total=Sum('grand_total'))['total'] or 0
    today_customers = User.objects.filter(
        date_joined__date=today,
        is_staff=False
    ).count()
    
    # Current hour metrics
    current_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
    hour_orders = Order.objects.filter(
        order_date__gte=current_hour,
        order_date__lt=current_hour + timedelta(hours=1)
    )
    hour_revenue = hour_orders.aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Recent activity
    recent_orders = Order.objects.select_related('user').order_by('-order_date')[:10]
    recent_reviews = ProductReview.objects.select_related('user', 'product').order_by('-date_added')[:10]
    
    context = {
        'today_revenue': today_revenue,
        'today_orders': today_orders.count(),
        'today_customers': today_customers,
        'hour_revenue': hour_revenue,
        'hour_orders': hour_orders.count(),
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
    }
    
    return render(request, 'accounts/real_time_analytics.html', context)
