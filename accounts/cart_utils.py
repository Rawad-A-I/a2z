"""
Cart utility functions for handling both anonymous and authenticated users.
"""
from django.contrib.sessions.models import Session
from .models import Cart, CartItem
from django.contrib.auth.models import User


def get_or_create_cart(request):
    """
    Get or create a cart for the current user (authenticated or anonymous).
    """
    if request.user.is_authenticated:
        # For authenticated users, use user-based cart
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_paid=False,
            defaults={'session_key': None}
        )
    else:
        # For anonymous users, use session-based cart
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            is_paid=False,
            defaults={'user': None}
        )
    
    return cart


def migrate_session_cart_to_user(request, user):
    """
    Migrate anonymous user's cart to authenticated user when they log in.
    """
    if not request.session.session_key:
        return None
    
    try:
        # Get the session-based cart
        session_cart = Cart.objects.get(
            session_key=request.session.session_key,
            is_paid=False
        )
        
        # Check if user already has a cart
        user_cart, user_cart_created = Cart.objects.get_or_create(
            user=user,
            is_paid=False,
            defaults={'session_key': None}
        )
        
        if not user_cart_created and session_cart.cart_items.exists():
            # User already has a cart, merge the items
            for session_item in session_cart.cart_items.all():
                existing_item = user_cart.cart_items.filter(
                    product=session_item.product,
                    size_variant=session_item.size_variant,
                    color_variant=session_item.color_variant
                ).first()
                
                if existing_item:
                    # Update quantity
                    existing_item.quantity += session_item.quantity
                    existing_item.save()
                else:
                    # Move item to user cart
                    session_item.cart = user_cart
                    session_item.save()
            
            # Delete the session cart
            session_cart.delete()
        elif user_cart_created:
            # User has no cart, transfer session cart to user
            session_cart.user = user
            session_cart.session_key = None
            session_cart.save()
        
        return user_cart
        
    except Cart.DoesNotExist:
        return None


def get_cart_count(request):
    """
    Get the total number of items in the cart.
    """
    try:
        cart = get_or_create_cart(request)
        return sum(item.quantity for item in cart.cart_items.all())
    except:
        return 0


def clear_session_cart(request):
    """
    Clear the session-based cart (useful after successful order).
    """
    if request.session.session_key:
        Cart.objects.filter(
            session_key=request.session.session_key,
            is_paid=False
        ).delete()
