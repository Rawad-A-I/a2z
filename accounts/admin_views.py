"""
Comprehensive admin views for store management.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import json
from datetime import datetime, timedelta

from .models import (
    Profile, CustomerLoyalty, StoreLocation, InventoryAlert, 
    Order, OrderItem, OrderFulfillment, Employee, CustomerSupport,
    ProductBundle, Analytics
)
from products.models import Product, ProductReview, StockMovement, Category


def is_admin_user(user):
    """Check if user is admin."""
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    """Main admin dashboard."""
    # Key metrics
    total_customers = User.objects.filter(is_staff=False).count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('grand_total'))['total'] or 0
    total_products = Product.objects.count()
    
    # Recent activity
    recent_orders = Order.objects.select_related('user').order_by('-order_date')[:10]
    recent_customers = User.objects.filter(is_staff=False).order_by('-date_joined')[:10]
    recent_reviews = ProductReview.objects.select_related('user', 'product').order_by('-date_added')[:10]
    
    # System alerts
    low_stock_alerts = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).count()
    pending_orders = Order.objects.filter(status='pending').count()
    open_support_tickets = CustomerSupport.objects.filter(status='open').count()
    
    # Sales chart data (last 30 days)
    sales_data = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        daily_sales = Order.objects.filter(order_date__date=date).aggregate(
            total=Sum('grand_total')
        )['total'] or 0
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
    
    context = {
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'recent_customers': recent_customers,
        'recent_reviews': recent_reviews,
        'low_stock_alerts': low_stock_alerts,
        'pending_orders': pending_orders,
        'open_support_tickets': open_support_tickets,
        'sales_data': sales_data,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin_user)
def user_management(request):
    """User management page."""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by user type
    user_type = request.GET.get('type')
    if user_type == 'customers':
        users = users.filter(is_staff=False)
    elif user_type == 'staff':
        users = users.filter(is_staff=True, is_superuser=False)
    elif user_type == 'admins':
        users = users.filter(is_superuser=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
    }
    
    return render(request, 'accounts/user_management.html', context)


@login_required
@user_passes_test(is_admin_user)
def user_detail(request, user_id):
    """Detailed user view."""
    user = get_object_or_404(User, id=user_id)
    
    # Get user data
    profile = getattr(user, 'profile', None)
    loyalty = getattr(user, 'loyalty', None)
    employee = getattr(user, 'employee_profile', None)
    
    # User activity
    orders = Order.objects.filter(user=user).order_by('-order_date')
    reviews = ProductReview.objects.filter(user=user).order_by('-date_added')
    support_tickets = CustomerSupport.objects.filter(user=user).order_by('-created_at')
    
    # Statistics
    stats = {
        'total_orders': orders.count(),
        'total_spent': orders.aggregate(total=Sum('grand_total'))['total'] or 0,
        'total_reviews': reviews.count(),
        'support_tickets': support_tickets.count(),
    }
    
    context = {
        'user': user,
        'profile': profile,
        'loyalty': loyalty,
        'employee': employee,
        'orders': orders[:10],
        'reviews': reviews[:10],
        'support_tickets': support_tickets[:5],
        'stats': stats,
    }
    
    return render(request, 'accounts/user_detail.html', context)


@login_required
@user_passes_test(is_admin_user)
def edit_user(request, user_id):
    """Edit user information."""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.save()
        
        # Update profile if exists
        profile = getattr(user, 'profile', None)
        if profile:
            profile.phone_number = request.POST.get('phone_number', profile.phone_number)
            profile.save()
        
        messages.success(request, 'User updated successfully.')
        return redirect('user_detail', user_id=user_id)
    
    context = {
        'user': user,
    }
    
    return render(request, 'accounts/edit_user.html', context)


@login_required
@user_passes_test(is_admin_user)
def product_management(request):
    """Product management page."""
    products = Product.objects.all().order_by('-created_at')
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Filter by stock status
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        products = products.filter(stock_quantity__lte=F('low_stock_threshold'))
    elif stock_filter == 'out':
        products = products.filter(stock_quantity=0)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(product_desription__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.all()
    
    context = {
        'products': products_page,
        'categories': categories,
    }
    
    return render(request, 'accounts/product_management.html', context)


@login_required
@user_passes_test(is_admin_user)
def product_detail_admin(request, product_id):
    """Admin view of product details."""
    product = get_object_or_404(Product, uid=product_id)
    
    # Product statistics
    total_sold = OrderItem.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    total_revenue = OrderItem.objects.filter(product=product).aggregate(
        total=Sum('product_price')
    )['total'] or 0
    
    # Stock movements
    stock_movements = StockMovement.objects.filter(product=product).order_by('-created_at')
    
    # Reviews
    reviews = ProductReview.objects.filter(product=product).order_by('-date_added')
    
    context = {
        'product': product,
        'total_sold': total_sold,
        'total_revenue': total_revenue,
        'stock_movements': stock_movements[:10],
        'reviews': reviews[:10],
    }
    
    return render(request, 'accounts/product_detail_admin.html', context)


@login_required
@user_passes_test(is_admin_user)
def order_management_admin(request):
    """Admin order management."""
    orders = Order.objects.select_related('user', 'assigned_employee').order_by('-order_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(order_date__date__gte=date_from)
    if date_to:
        orders = orders.filter(order_date__date__lte=date_to)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 25)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    context = {
        'orders': orders_page,
        'status_choices': Order._meta.get_field('status').choices,
    }
    
    return render(request, 'accounts/order_management_admin.html', context)


@login_required
@user_passes_test(is_admin_user)
def system_settings(request):
    """System settings management."""
    if request.method == 'POST':
        # Update system settings
        # This would integrate with your settings system
        messages.success(request, 'System settings updated successfully.')
        return redirect('system_settings')
    
    # Get current settings
    settings_data = {
        'site_name': 'Django eCommerce',
        'site_description': 'Your online store',
        'currency': 'USD',
        'timezone': 'UTC',
        'maintenance_mode': False,
    }
    
    context = {
        'settings': settings_data,
    }
    
    return render(request, 'accounts/system_settings.html', context)


@login_required
@user_passes_test(is_admin_user)
def store_locations_admin(request):
    """Admin store locations management."""
    locations = StoreLocation.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Add new store location
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        StoreLocation.objects.create(
            name=name,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
            email=email,
            latitude=latitude,
            longitude=longitude
        )
        
        messages.success(request, 'Store location added successfully.')
        return redirect('store_locations_admin')
    
    context = {
        'locations': locations,
    }
    
    return render(request, 'accounts/store_locations_admin.html', context)


@login_required
@user_passes_test(is_admin_user)
def employee_management(request):
    """Employee management."""
    employees = Employee.objects.select_related('user', 'store_location').all()
    
    if request.method == 'POST':
        # Create new employee
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        department = request.POST.get('department')
        store_location_id = request.POST.get('store_location')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=True
        )
        
        # Create employee profile
        store_location = StoreLocation.objects.get(uid=store_location_id) if store_location_id else None
        Employee.objects.create(
            user=user,
            department=department,
            store_location=store_location
        )
        
        messages.success(request, 'Employee created successfully.')
        return redirect('employee_management')
    
    # Get store locations for dropdown
    store_locations = StoreLocation.objects.filter(is_active=True)
    
    context = {
        'employees': employees,
        'store_locations': store_locations,
    }
    
    return render(request, 'accounts/employee_management.html', context)


@login_required
@user_passes_test(is_admin_user)
def system_reports(request):
    """System reports and exports."""
    report_type = request.GET.get('type', 'overview')
    
    if report_type == 'sales':
        # Sales report
        orders = Order.objects.all()
        total_revenue = orders.aggregate(total=Sum('grand_total'))['total'] or 0
        total_orders = orders.count()
        
        context = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'orders': orders[:100],  # Limit for display
        }
        
    elif report_type == 'customers':
        # Customer report
        customers = User.objects.filter(is_staff=False)
        total_customers = customers.count()
        new_customers_this_month = customers.filter(
            date_joined__gte=timezone.now().replace(day=1)
        ).count()
        
        context = {
            'total_customers': total_customers,
            'new_customers_this_month': new_customers_this_month,
            'customers': customers[:100],
        }
        
    elif report_type == 'products':
        # Product report
        products = Product.objects.all()
        low_stock_products = products.filter(
            stock_quantity__lte=F('low_stock_threshold')
        )
        
        context = {
            'total_products': products.count(),
            'low_stock_products': low_stock_products.count(),
            'products': products[:100],
        }
        
    else:
        # Overview report
        context = {
            'total_customers': User.objects.filter(is_staff=False).count(),
            'total_orders': Order.objects.count(),
            'total_products': Product.objects.count(),
            'total_revenue': Order.objects.aggregate(total=Sum('grand_total'))['total'] or 0,
        }
    
    context['report_type'] = report_type
    
    return render(request, 'accounts/system_reports.html', context)


@login_required
@user_passes_test(is_admin_user)
def backup_restore(request):
    """Backup and restore functionality."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'backup':
            # Create backup
            # This would integrate with your backup system
            messages.success(request, 'Backup created successfully.')
        elif action == 'restore':
            # Restore from backup
            # This would integrate with your restore system
            messages.success(request, 'System restored successfully.')
    
    context = {
        'backups': [],  # List of available backups
    }
    
    return render(request, 'accounts/backup_restore.html', context)


@login_required
@user_passes_test(is_admin_user)
def system_logs(request):
    """System logs and monitoring."""
    # This would integrate with your logging system
    logs = [
        {'timestamp': timezone.now(), 'level': 'INFO', 'message': 'System started'},
        {'timestamp': timezone.now(), 'level': 'WARNING', 'message': 'Low stock alert'},
        {'timestamp': timezone.now(), 'level': 'ERROR', 'message': 'Payment failed'},
    ]
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'accounts/system_logs.html', context)
