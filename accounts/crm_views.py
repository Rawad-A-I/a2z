"""
Customer Relationship Management (CRM) views.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from datetime import datetime, timedelta

from .models import CustomerLoyalty, CustomerSupport, Order, Profile
from products.models import Product, ProductReview
from accounts.models import Wishlist, RecentlyViewed


def is_staff_user(user):
    """Check if user is staff member."""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def crm_dashboard(request):
    """CRM dashboard with customer analytics."""
    # Customer statistics
    total_customers = User.objects.filter(is_staff=False).count()
    new_customers_this_month = User.objects.filter(
        date_joined__gte=timezone.now().replace(day=1),
        is_staff=False
    ).count()
    
    # Customer loyalty statistics
    loyalty_stats = {
        'bronze': CustomerLoyalty.objects.filter(tier='bronze').count(),
        'silver': CustomerLoyalty.objects.filter(tier='silver').count(),
        'gold': CustomerLoyalty.objects.filter(tier='gold').count(),
        'platinum': CustomerLoyalty.objects.filter(tier='platinum').count(),
    }
    
    # Top customers by spending
    top_customers = CustomerLoyalty.objects.order_by('-total_spent')[:10]
    
    # Recent customer activity
    recent_orders = Order.objects.select_related('user').order_by('-order_date')[:10]
    recent_reviews = ProductReview.objects.select_related('user', 'product').order_by('-date_added')[:10]
    
    # Customer support statistics
    support_stats = {
        'open_tickets': CustomerSupport.objects.filter(status='open').count(),
        'in_progress': CustomerSupport.objects.filter(status='in_progress').count(),
        'resolved': CustomerSupport.objects.filter(status='resolved').count(),
    }
    
    context = {
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'loyalty_stats': loyalty_stats,
        'top_customers': top_customers,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'support_stats': support_stats,
    }
    
    return render(request, 'accounts/crm_dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def customer_list(request):
    """List all customers with filtering and search."""
    customers = User.objects.filter(is_staff=False).select_related('profile', 'loyalty').order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by loyalty tier
    tier_filter = request.GET.get('tier')
    if tier_filter:
        customers = customers.filter(loyalty__tier=tier_filter)
    
    # Filter by registration date
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        customers = customers.filter(date_joined__date__gte=date_from)
    if date_to:
        customers = customers.filter(date_joined__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(customers, 25)
    page_number = request.GET.get('page')
    customers_page = paginator.get_page(page_number)
    
    context = {
        'customers': customers_page,
        'tier_choices': CustomerLoyalty._meta.get_field('tier').choices,
    }
    
    return render(request, 'accounts/customer_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def customer_detail(request, user_id):
    """Detailed customer view."""
    customer = get_object_or_404(User, id=user_id)
    
    # Get customer data
    profile = getattr(customer, 'profile', None)
    loyalty = getattr(customer, 'loyalty', None)
    
    # Customer orders
    orders = Order.objects.filter(user=customer).order_by('-order_date')
    
    # Customer reviews
    reviews = ProductReview.objects.filter(user=customer).order_by('-date_added')
    
    # Customer wishlist
    wishlist = Wishlist.objects.filter(user=customer).select_related('product')
    
    # Recently viewed products
    recently_viewed = RecentlyViewed.objects.filter(user=customer).select_related('product')
    
    # Customer support tickets
    support_tickets = CustomerSupport.objects.filter(user=customer).order_by('-created_at')
    
    # Order statistics
    order_stats = {
        'total_orders': orders.count(),
        'total_spent': orders.aggregate(total=Sum('grand_total'))['total'] or 0,
        'average_order_value': orders.aggregate(avg=Avg('grand_total'))['avg'] or 0,
        'last_order': orders.first().order_date if orders.exists() else None,
    }
    
    context = {
        'customer': customer,
        'profile': profile,
        'loyalty': loyalty,
        'orders': orders[:10],  # Show last 10 orders
        'reviews': reviews[:10],  # Show last 10 reviews
        'wishlist': wishlist[:10],  # Show first 10 wishlist items
        'recently_viewed': recently_viewed[:10],  # Show last 10 viewed
        'support_tickets': support_tickets[:5],  # Show last 5 tickets
        'order_stats': order_stats,
    }
    
    return render(request, 'accounts/customer_detail.html', context)


@login_required
@user_passes_test(is_staff_user)
def customer_segments(request):
    """Customer segmentation analysis."""
    # High-value customers (top 20% by spending)
    high_value_threshold = CustomerLoyalty.objects.order_by('-total_spent').values_list('total_spent', flat=True)
    if high_value_threshold:
        threshold = high_value_threshold[int(len(high_value_threshold) * 0.2)] if len(high_value_threshold) > 5 else 0
        high_value_customers = CustomerLoyalty.objects.filter(total_spent__gte=threshold)
    else:
        high_value_customers = CustomerLoyalty.objects.none()
    
    # Frequent customers (multiple orders)
    frequent_customers = User.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gte=3, is_staff=False)
    
    # New customers (registered in last 30 days)
    new_customers = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30),
        is_staff=False
    )
    
    # Inactive customers (no orders in last 90 days)
    inactive_customers = User.objects.filter(
        is_staff=False
    ).exclude(
        orders__order_date__gte=timezone.now() - timedelta(days=90)
    ).distinct()
    
    context = {
        'high_value_customers': high_value_customers,
        'frequent_customers': frequent_customers,
        'new_customers': new_customers,
        'inactive_customers': inactive_customers,
    }
    
    return render(request, 'accounts/customer_segments.html', context)


@login_required
@user_passes_test(is_staff_user)
def customer_support(request):
    """Customer support ticket management."""
    tickets = CustomerSupport.objects.select_related('user', 'assigned_to').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    # Filter by assigned user
    assigned_filter = request.GET.get('assigned')
    if assigned_filter:
        tickets = tickets.filter(assigned_to_id=assigned_filter)
    
    # Pagination
    paginator = Paginator(tickets, 25)
    page_number = request.GET.get('page')
    tickets_page = paginator.get_page(page_number)
    
    # Get staff users for assignment
    staff_users = User.objects.filter(is_staff=True)
    
    context = {
        'tickets': tickets_page,
        'staff_users': staff_users,
        'status_choices': CustomerSupport._meta.get_field('status').choices,
        'priority_choices': CustomerSupport._meta.get_field('priority').choices,
    }
    
    return render(request, 'accounts/customer_support.html', context)


@login_required
@user_passes_test(is_staff_user)
def support_ticket_detail(request, ticket_id):
    """View and manage support ticket."""
    ticket = get_object_or_404(CustomerSupport, uid=ticket_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign':
            assigned_to_id = request.POST.get('assigned_to')
            if assigned_to_id:
                ticket.assigned_to_id = assigned_to_id
                ticket.status = 'in_progress'
                ticket.save()
                messages.success(request, 'Ticket assigned successfully.')
        
        elif action == 'update_status':
            new_status = request.POST.get('status')
            ticket.status = new_status
            if new_status == 'resolved':
                ticket.resolved_at = timezone.now()
            ticket.save()
            messages.success(request, 'Ticket status updated.')
        
        elif action == 'add_resolution':
            resolution = request.POST.get('resolution')
            ticket.resolution = resolution
            ticket.status = 'resolved'
            ticket.resolved_at = timezone.now()
            ticket.save()
            messages.success(request, 'Resolution added.')
        
        return redirect('support_ticket_detail', ticket_id=ticket_id)
    
    # Get staff users for assignment
    staff_users = User.objects.filter(is_staff=True)
    
    context = {
        'ticket': ticket,
        'staff_users': staff_users,
        'status_choices': CustomerSupport._meta.get_field('status').choices,
    }
    
    return render(request, 'accounts/support_ticket_detail.html', context)


@login_required
def create_support_ticket(request):
    """Create a new support ticket."""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        priority = request.POST.get('priority', 'medium')
        
        CustomerSupport.objects.create(
            user=request.user,
            subject=subject,
            message=message,
            priority=priority
        )
        
        messages.success(request, 'Support ticket created successfully.')
        return redirect('customer_support')
    
    context = {
        'priority_choices': CustomerSupport._meta.get_field('priority').choices,
    }
    
    return render(request, 'accounts/create_support_ticket.html', context)


@login_required
def my_support_tickets(request):
    """View user's own support tickets."""
    tickets = CustomerSupport.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'tickets': tickets,
    }
    
    return render(request, 'accounts/my_support_tickets.html', context)


@login_required
@user_passes_test(is_staff_user)
def customer_analytics(request):
    """Customer analytics and insights."""
    # Customer acquisition over time
    customer_acquisition = []
    for i in range(12):  # Last 12 months
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = User.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end,
            is_staff=False
        ).count()
        customer_acquisition.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    # Customer lifetime value analysis
    lifetime_values = CustomerLoyalty.objects.values('tier').annotate(
        avg_spent=Avg('total_spent'),
        count=Count('id')
    ).order_by('-avg_spent')
    
    # Customer retention analysis
    total_customers = User.objects.filter(is_staff=False).count()
    repeat_customers = User.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=1, is_staff=False).count()
    
    retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    context = {
        'customer_acquisition': customer_acquisition,
        'lifetime_values': lifetime_values,
        'retention_rate': retention_rate,
        'total_customers': total_customers,
        'repeat_customers': repeat_customers,
    }
    
    return render(request, 'accounts/customer_analytics.html', context)
