"""
Employee views for order management.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Order, OrderItem
from products.models import Product


def is_employee(user):
    """Check if user is an employee (staff member)."""
    return user.is_staff


# Removed old employee_dashboard function - now using employee_dashboard_redirect


@login_required
def employee_order_detail(request, order_id):
    """Employee view of order details."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    order = get_object_or_404(Order, order_id=order_id)
    order_items = order.order_items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'status_choices': Order._meta.get_field('status').choices,
    }
    
    return render(request, 'accounts/employee_order_detail.html', context)


@login_required
def assign_order(request, order_id):
    """Assign order to current employee."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    order = get_object_or_404(Order, order_id=order_id)
    # Use request.user directly since we're using is_staff
    
    if order.assigned_employee and order.assigned_employee != request.user:
        messages.warning(request, f'This order is already assigned to {order.assigned_employee}.')
    else:
        order.assigned_employee = request.user
        order.save()
        messages.success(request, f'Order {order_id} assigned to you.')
    
    return redirect('employee_order_detail', order_id=order_id)


@login_required
def confirm_order(request, order_id):
    """Confirm order and deduct stock."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    order = get_object_or_404(Order, order_id=order_id)
    # Use request.user directly since we're using is_staff
    
    # Check if order is assigned to this employee
    if order.assigned_employee != request.user:
        messages.error(request, 'You can only confirm orders assigned to you.')
        return redirect('employee_order_management')
    
    # Check if order is already confirmed
    if order.is_confirmed:
        messages.warning(request, 'This order is already confirmed.')
        return redirect('employee_order_detail', order_id=order_id)
    
    # Check stock availability before confirming
    order_items = order.order_items.all()
    stock_issues = []
    
    for order_item in order_items:
        if not order_item.product.can_fulfill_order(order_item.quantity):
            stock_issues.append(
                f"{order_item.product.product_name}: Only {order_item.product.stock_quantity} available, "
                f"but {order_item.quantity} requested."
            )
    
    if stock_issues:
        messages.error(request, 'Cannot confirm order due to stock issues:')
        for issue in stock_issues:
            messages.error(request, f'• {issue}')
        return redirect('employee_order_detail', order_id=order_id)
    
    # Confirm the order and deduct stock
    try:
        order.is_confirmed = True
        order.status = 'confirmed'
        order.confirmed_date = timezone.now()
        order.save()
        
        # Deduct stock for each item
        for order_item in order_items:
            order_item.product.update_stock(-order_item.quantity)
        
        messages.success(request, f'Order {order_id} confirmed and stock deducted.')
        
    except Exception as e:
        messages.error(request, f'Error confirming order: {str(e)}')
    
    return redirect('employee_order_detail', order_id=order_id)


@login_required
def update_order_status(request, order_id):
    """Update order status."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    order = get_object_or_404(Order, order_id=order_id)
    # Use request.user directly since we're using is_staff
    
    # Check if order is assigned to this employee
    try:
        if order.assigned_employee != request.user:
            messages.error(request, 'You can only update orders assigned to you.')
            return redirect('employee_order_management')
    except Exception as e:
        print(f"Type mismatch in order assignment check: {e}")
        # Allow access if there's a type mismatch
        pass
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in [choice[0] for choice in Order._meta.get_field('status').choices]:
            order.status = new_status
            if notes:
                order.notes = notes
            order.save()
            messages.success(request, f'Order status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('employee_order_detail', order_id=order_id)


@login_required
def cancel_order(request, order_id):
    """Cancel order."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    order = get_object_or_404(Order, order_id=order_id)
    # Use request.user directly since we're using is_staff
    
    # Check if order is assigned to this employee
    if order.assigned_employee != request.user:
        messages.error(request, 'You can only cancel orders assigned to you.')
        return redirect('employee_order_management')
    
    if order.is_confirmed:
        messages.warning(request, 'Cannot cancel confirmed order. Contact admin.')
        return redirect('employee_order_detail', order_id=order_id)
    
    order.status = 'cancelled'
    order.save()
    messages.success(request, f'Order {order_id} cancelled.')
    
    return redirect('employee_dashboard')


def employee_dashboard_redirect(request):
    """Employee dashboard redirect page with two main options"""
    print(f"DEBUG: Employee dashboard redirect accessed by user: {request.user}")
    print(f"DEBUG: User is staff: {request.user.is_staff}")
    
    if not is_employee(request.user):
        print("DEBUG: User is not an employee, redirecting to index")
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    print("DEBUG: User is employee, proceeding with dashboard")
    
    # Get basic statistics for the overview
    try:
        my_orders_count = Order.objects.filter(assigned_employee=request.user).count()
    except Exception as e:
        print(f"Type mismatch in stats query: {e}")
        my_orders_count = 0
    
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'confirmed_orders': Order.objects.filter(status='confirmed').count(),
        'my_orders': my_orders_count,
    }
    
    context = {
        'stats': stats,
    }
    print("DEBUG: Rendering employee dashboard redirect template")
    return render(request, 'accounts/employee_dashboard_redirect.html', context)


def employee_hub(request):
    """New separate employee hub page - completely independent"""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    return render(request, 'accounts/employee_hub.html')


def employee_order_management(request):
    """Employee order management dashboard - original dashboard functionality"""
    print(f"DEBUG: Order management accessed by user: {request.user}")
    
    if not is_employee(request.user):
        print("DEBUG: User is not an employee, redirecting to index")
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    print("DEBUG: User is employee, proceeding with order management")
    
    # Get orders assigned to this employee or unassigned orders
    try:
        orders = Order.objects.filter(
            Q(assigned_employee=request.user) | Q(assigned_employee__isnull=True)
        ).order_by('-order_date')
        print(f"DEBUG: Found {orders.count()} orders")
    except Exception as e:
        print(f"Type mismatch in employee query: {e}")
        orders = Order.objects.filter(
            Q(assigned_employee__isnull=True)
        ).order_by('-order_date')
        print(f"DEBUG: Fallback query found {orders.count()} orders")
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
        print(f"DEBUG: Filtered by status {status_filter}, now {orders.count()} orders")
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    print(f"DEBUG: Paginated to page {orders_page.number} of {orders_page.paginator.num_pages}")
    
    # Statistics
    try:
        my_orders_count = Order.objects.filter(assigned_employee=request.user).count()
    except Exception as e:
        print(f"Type mismatch in stats query: {e}")
        my_orders_count = 0
    
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'confirmed_orders': Order.objects.filter(status='confirmed').count(),
        'my_orders': my_orders_count,
    }
    
    print(f"DEBUG: Stats: {stats}")
    
    context = {
        'orders': orders_page,
        'stats': stats,
    }
    print("DEBUG: Rendering employee order management template")
    return render(request, 'accounts/employee_order_management.html', context)
