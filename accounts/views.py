import os
import json
import uuid
# Temporarily disable WeasyPrint to fix deployment
# from weasyprint import CSS, HTML
from django.utils import timezone
from products.models import *
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from home.models import ShippingAddress
from django.contrib.auth.models import User
from django.template.loader import get_template
from accounts.models import Profile, Cart, CartItem, Order, OrderItem
from base.emails import send_account_activation_email
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect, render, get_object_or_404
from accounts.forms import UserUpdateForm, UserProfileForm, ShippingAddressForm, CustomPasswordChangeForm


# Create your views here.

def accounts_dashboard(request):
    """Accounts dashboard - redirect to login if not authenticated"""
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    else:
        return redirect('login')

def account_login_page(request):
    """Dedicated account login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.warning(request, 'Account not found!')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=username, password=password)
        if user_obj:
            # Check if user is staff (has staff privileges)
            if user_obj.is_staff:
                login(request, user_obj)
                messages.success(request, 'Account login successful!')
                return redirect('employee_hub')
            else:
                messages.error(request, 'This account is not authorized for employee access. Please contact administrator.')
                return HttpResponseRedirect(request.path_info)
        else:
            messages.error(request, 'Invalid credentials!')
            return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/employee_login.html')


def login_page(request):
    next_url = request.GET.get('next') # Get the next URL from the query parameter
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.warning(request, 'Account not found!')
            return HttpResponseRedirect(request.path_info)

        # Skip email verification check for simple setup
        # if not user_obj[0].profile.is_email_verified:
        #     messages.error(request, 'Account not verified! Please check your email and click the verification link.')
        #     return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=username, password=password)
        if user_obj:
            login(request, user_obj)
            messages.success(request, 'Login Successfull.')

            # Check if the next URL is safe and not empty
            if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts=request.get_host()):
                return redirect(next_url)
            else:
                return redirect('index')

        messages.warning(request, 'Invalid credentials.')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username, email=email)

        if user_obj.exists():
            messages.info(request, 'Username or email already exists!')
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create(
            username=username, first_name=first_name, last_name=last_name, email=email)
        user_obj.set_password(password)
        user_obj.save()

        profile = Profile.objects.get(user=user_obj)
        profile.email_token = str(uuid.uuid4())
        profile.is_email_verified = True  # Auto-verify for development
        profile.save()

        # Skip email sending for development
        # send_account_activation_email(email, profile.email_token)
        messages.success(request, "Account created successfully! You can now login.")
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')


@login_required
def user_logout(request):
    logout(request)
    messages.warning(request, "Logged Out Successfully!")
    return redirect('index')


def activate_email_account(request, email_token):
    try:
        profile = Profile.objects.get(email_token=email_token)
        if profile.is_email_verified:
            messages.info(request, 'Your account is already verified.')
            return redirect('login')
        
        profile.is_email_verified = True
        profile.save()
        messages.success(request, 'Account verification successful! You can now login.')
        return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('register')
    except Exception as e:
        messages.error(request, 'An error occurred during verification.')
        return redirect('register')


def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            
            if profile.is_email_verified:
                messages.info(request, 'Your account is already verified.')
                return redirect('login')
            
            # Generate new token
            profile.email_token = str(uuid.uuid4())
            profile.save()
            
            # Send new verification email
            send_account_activation_email(email, profile.email_token)
            messages.success(request, 'Verification email sent! Please check your inbox.')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('login')
    
    return redirect('login')


def add_to_cart(request, uid):
    try:
        variant = request.GET.get('size')
        quantity = int(request.GET.get('quantity', 1))  # Get quantity from URL parameter
        product = get_object_or_404(Product, uid=uid)
        
        # Validate quantity
        if quantity < 1:
            quantity = 1
        
        # Check if product has size variants
        has_size_variants = product.size_variant.exists()
        
        # If product has size variants but no size selected, show warning
        if has_size_variants and not variant:
            messages.warning(request, 'Please select a size variant!')
            return redirect(request.META.get('HTTP_REFERER'))
        
        # Check stock availability
        if not product.is_in_stock:
            messages.error(request, 'This product is currently out of stock.')
            return redirect(request.META.get('HTTP_REFERER'))
        
        if product.is_low_stock():
            messages.warning(request, 'Only a few items left in stock!')
        
        # Check if we can fulfill the requested quantity
        if not product.can_fulfill_order(quantity):
            messages.error(request, 'Not enough stock available. Only {} items left.'.format(product.stock_quantity))
            return redirect(request.META.get('HTTP_REFERER'))
        
        from .cart_utils import get_or_create_cart
        cart = get_or_create_cart(request)
        
        # Handle size variant if product has sizes
        size_variant = None
        if has_size_variants and variant:
            try:
                size_variant = get_object_or_404(SizeVariant, size_name=variant)
            except:
                messages.error(request, 'Invalid size variant selected!')
                return redirect(request.META.get('HTTP_REFERER'))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, size_variant=size_variant)
        
        if not created:
            # Update existing cart item with new quantity
            cart_item.quantity = quantity
            cart_item.save()
        else:
            # Set initial quantity for new cart item
            cart_item.quantity = quantity
            cart_item.save()

        messages.success(request, f'{quantity} item(s) added to cart successfully.')

    except Exception as e:
        messages.error(request, 'Error adding item to cart: ' + str(e))

    return redirect(reverse('cart'))


def cart(request):
    from .cart_utils import get_or_create_cart
    
    try:
        cart_obj = get_or_create_cart(request)
    except Exception as e:
        messages.error(request, "Error loading cart. Please try again.")
        return redirect('products_only')

    if request.method == 'POST':
        # Check if user is authenticated for checkout
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to proceed with checkout.')
            return redirect('login')
        
        # Apply coupon if any
        coupon = request.POST.get('coupon')
        if coupon:
            coupon_obj = Coupon.objects.filter(coupon_code__exact=coupon).first()
            if not coupon_obj:
                messages.warning(request, 'Invalid coupon code.')
            elif cart_obj.coupon:
                messages.warning(request, 'Coupon already exists.')
            elif coupon_obj.is_expired:
                messages.warning(request, 'Coupon code expired.')
            elif cart_obj.get_cart_total() < coupon_obj.minimum_amount:
                messages.warning(request, f'Amount should be greater than {coupon_obj.minimum_amount}')
            else:
                cart_obj.coupon = coupon_obj
                cart_obj.save()
                messages.success(request, 'Coupon applied successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Check if user has verified their address with map and phone number
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.latitude or not profile.longitude:
            messages.error(request, 'Please verify your address using the map before placing an order.')
            return redirect('address_management')
        
        # Check if user has provided phone number
        if not profile.phone_number:
            messages.error(request, 'Please add your phone number to your profile before placing an order.')
            return redirect('profile', username=request.user.username)
        
        # Create the order for COD
        order = create_order(cart_obj)
        cart_obj.is_paid = True  # Mark as paid for COD
        cart_obj.save()
        messages.success(request, 'Order placed successfully! Pay on delivery.')
        return redirect('order_details', order_id=order.order_id)

    context = {
        'cart': cart_obj,
        'quantity_range': range(1, 6),
    }
    return render(request, 'accounts/cart.html', context)


@require_POST
@login_required
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        cart_item_id = data.get("cart_item_id")
        quantity = int(data.get("quantity"))

        cart_item = CartItem.objects.get(uid=cart_item_id, cart__user=request.user, cart__is_paid=False)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def remove_cart(request, uid):
    try:
        cart_item = get_object_or_404(CartItem, uid=uid)
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')

    except Exception as e:
        print(e)
        messages.warning(request, 'Error removing item from cart.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid=cart_id)
    cart.coupon = None
    cart.save()

    messages.success(request, 'Coupon Removed.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




# HTML to PDF Conversion - Temporarily disabled due to WeasyPrint dependencies
def render_to_pdf(template_src, context_dict={}):
    # Temporarily return a simple text response instead of PDF
    # TODO: Fix WeasyPrint system dependencies for PDF generation
    response = HttpResponse(
        f"PDF generation temporarily disabled. Order ID: {context_dict.get('order', {}).order_id if context_dict.get('order') else 'N/A'}",
        content_type='text/plain'
    )
    response['Content-Disposition'] = f'attachment; filename="invoice_{context_dict.get("order", {}).order_id if context_dict.get("order") else "unknown"}.txt"'
    return response


def download_invoice(request, order_id):
    order = Order.objects.filter(order_id=order_id).first()
    order_items = order.order_items.all()

    context = {
        'order': order,
        'order_items': order_items,
    }

    pdf = render_to_pdf('accounts/order_pdf_generate.html', context)
    if pdf:
        return pdf
    return HttpResponse("Error generating PDF", status=400)


@login_required
def profile_view(request, username):
    user_name = get_object_or_404(User, username=username)
    user = request.user
    profile = user.profile

    user_form = UserUpdateForm(instance=user)
    profile_form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        'user_name': user_name,
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def update_shipping_address(request):
    shipping_address = ShippingAddress.objects.filter(
        user=request.user, current_address=True).first()

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.current_address = True
            shipping_address.save()

            messages.success(request, "The Address Has Been Successfully Saved/Updated!")

            form = ShippingAddressForm()
        else:
            form = ShippingAddressForm(request.POST, instance=shipping_address)
    else:
        form = ShippingAddressForm(instance=shipping_address)

    return render(request, 'accounts/shipping_address_form.html', {'form': form})


# Order history view
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'accounts/order_history.html', {'orders': orders})


# Create an order view
def create_order(cart):
    # Generate a unique order ID for COD orders
    import uuid
    order_id = f"COD_{uuid.uuid4().hex[:8].upper()}"
    
    # Check stock availability before creating order (but don't deduct yet)
    cart_items = CartItem.objects.filter(cart=cart)
    for cart_item in cart_items:
        if not cart_item.product.can_fulfill_order(cart_item.quantity):
            raise ValueError(f"Not enough stock for {cart_item.product.product_name}. Only {cart_item.product.stock_quantity} available.")
    
    order, created = Order.objects.get_or_create(
        user=cart.user,
        order_id=order_id,
        payment_status="Pending",
        shipping_address=cart.user.profile.shipping_address,
        payment_mode="Cash on Delivery",
        order_total_price=cart.get_cart_total(),
        coupon=cart.coupon,
        grand_total=cart.get_cart_total_price_after_coupon(),
        status='pending',  # Order starts as pending
        is_confirmed=False,  # Not confirmed yet
    )

    # Create OrderItem instances (but don't deduct stock yet)
    for cart_item in cart_items:
        OrderItem.objects.get_or_create(
            order=order,
            product=cart_item.product,
            size_variant=cart_item.size_variant,
            color_variant=cart_item.color_variant,
            quantity=cart_item.quantity,
            product_price=cart_item.get_product_price()
        )
        
        # NOTE: Stock will be deducted only when employee confirms the order

    return order


# Order Details view
@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
        'order_total_price': sum(item.get_total_price() for item in order_items),
        'coupon_discount': order.coupon.discount_amount if order.coupon else 0,
        'grand_total': order.get_order_total_price()
    }
    return render(request, 'accounts/order_details.html', context)


# Order Tracking view - dedicated page for tracking order progress
@login_required
def order_tracking(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    # Calculate progress percentage
    progress_percentage = 0
    if order.status == 'pending':
        progress_percentage = 20
    elif order.status == 'confirmed':
        progress_percentage = 40
    elif order.status == 'processing':
        progress_percentage = 60
    elif order.status == 'shipped':
        progress_percentage = 80
    elif order.status == 'delivered':
        progress_percentage = 100
    elif order.status == 'cancelled':
        progress_percentage = 0
    
    context = {
        'order': order,
        'order_items': order_items,
        'progress_percentage': progress_percentage,
        'order_total_price': sum(item.get_total_price() for item in order_items),
        'coupon_discount': order.coupon.discount_amount if order.coupon else 0,
        'grand_total': order.get_order_total_price()
    }
    return render(request, 'accounts/order_tracking.html', context)


# Delete user account feature
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('index')


def checkout(request):
    """
    Checkout view - creates an order from the cart and redirects to order details.
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to proceed with checkout.')
        return redirect('login')
    
    try:
        from .cart_utils import get_or_create_cart
        cart = get_or_create_cart(request)
        
        # Check if cart has items
        if not cart.cart_items.exists():
            messages.warning(request, "Your cart is empty. Add some items before checkout.")
            return redirect('cart')
        
        # Create order from cart
        order = create_order(cart)
        
        # Mark cart as paid
        cart.is_paid = True
        cart.save()
        
        messages.success(request, f"Order created successfully! Order ID: {order.order_id}")
        return redirect('order_details', order_id=order.order_id)
        
    except Exception as e:
        messages.error(request, f"Error creating order: {str(e)}")
        return redirect('cart')


# Account Settings Views
from accounts.models import (
    UserPreferences, UserSession, TwoFactorAuth, ConnectedAccount,
    AccountActivity, SecurityQuestion, EmailVerification, PhoneVerification
)
from accounts.forms import (
    PersonalInfoForm, PasswordChangeForm, NotificationPreferencesForm,
    PhoneVerificationForm
)


@login_required
def account_settings(request):
    """Main account settings page - detects if mobile/webapp."""
    # Check if user is on mobile/webapp
    is_mobile = request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    
    if is_mobile:
        return render(request, 'accounts/settings/account_settings.html')
    else:
        return render(request, 'accounts/modern_account_page.html')


@login_required
def personal_information(request):
    """Personal information settings."""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, request.FILES, instance=preferences)
        if form.is_valid():
            form.save()
            
            # Log activity
            AccountActivity.objects.create(
                user=request.user,
                activity_type='profile_updated',
                description='Personal information updated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Personal information updated successfully!')
            return redirect('personal_information')
    else:
        form = PersonalInfoForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/personal_information.html', context)


@login_required
def login_security(request):
    """Login and security settings."""
    # Get user sessions
    sessions = UserSession.objects.filter(user=request.user, is_active=True).order_by('-last_activity')
    
    # Get 2FA status
    two_factor, created = TwoFactorAuth.objects.get_or_create(user=request.user)
    
    # Get connected accounts
    connected_accounts = ConnectedAccount.objects.filter(user=request.user)
    
    # Get recent security activities
    activities = AccountActivity.objects.filter(
        user=request.user,
        activity_type__in=['login', 'password_change', 'email_change', '2fa_enabled', '2fa_disabled']
    ).order_by('-created_at')[:10]
    
    context = {
        'sessions': sessions,
        'two_factor': two_factor,
        'connected_accounts': connected_accounts,
        'activities': activities,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/login_security.html', context)


@login_required
@require_POST
def change_password(request):
    """Change user password."""
    form = PasswordChangeForm(request.user, request.POST)
    
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        
        # Log activity
        AccountActivity.objects.create(
            user=request.user,
            activity_type='password_change',
            description='Password changed successfully',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, 'Password changed successfully!')
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required
@require_POST
def revoke_session(request, session_id):
    """Revoke a specific session."""
    session = get_object_or_404(UserSession, id=session_id, user=request.user)
    session.is_active = False
    session.save()
    
    # Log activity
    AccountActivity.objects.create(
        user=request.user,
        activity_type='logout',
        description=f'Session revoked for {session.device_name or "Unknown Device"}',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    messages.success(request, 'Session revoked successfully!')
    return redirect('login_security')


@login_required
def notification_preferences(request):
    """Notification preferences settings."""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated!')
            return redirect('notification_preferences')
    else:
        form = NotificationPreferencesForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/notification_preferences.html', context)


@login_required
@require_POST
def update_notification_preference(request):
    """Update notification preference via AJAX."""
    preference = request.POST.get('preference')
    value = request.POST.get('value') == 'true'
    
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if hasattr(preferences, preference):
        setattr(preferences, preference, value)
        preferences.save()
        
        return JsonResponse({'success': True, 'value': value})
    
    return JsonResponse({'success': False, 'error': 'Invalid preference'})


@login_required
def connected_accounts(request):
    """Connected accounts management."""
    connected_accounts = ConnectedAccount.objects.filter(user=request.user)
    
    context = {
        'connected_accounts': connected_accounts,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/connected_accounts.html', context)


@login_required
@require_POST
def disconnect_account(request, account_id):
    """Disconnect a connected account."""
    account = get_object_or_404(ConnectedAccount, id=account_id, user=request.user)
    
    # Check if this is the primary account
    if account.is_primary:
        return JsonResponse({'success': False, 'error': 'Cannot disconnect primary account'})
    
    account.delete()
    
    # Log activity
    AccountActivity.objects.create(
        user=request.user,
        activity_type='profile_updated',
        description=f'Disconnected {account.provider.title()} account',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    messages.success(request, f'{account.provider.title()} account disconnected!')
    return redirect('connected_accounts')


@login_required
def two_factor_setup(request):
    """Setup two-factor authentication."""
    two_factor, created = TwoFactorAuth.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        method = request.POST.get('method')
        
        if method == 'sms':
            # Generate SMS verification code
            phone_number = request.POST.get('phone_number')
            if phone_number:
                # Create phone verification
                import secrets
                code = secrets.randbelow(900000) + 100000  # 6-digit code
                PhoneVerification.objects.create(
                    user=request.user,
                    phone_number=phone_number,
                    code=str(code),
                    expires_at=timezone.now() + timezone.timedelta(minutes=10)
                )
                
                # TODO: Send SMS with code
                messages.info(request, f'Verification code sent to {phone_number}')
                return redirect('verify_phone_2fa')
        
        elif method == 'email':
            # Generate email verification
            token = uuid.uuid4()
            EmailVerification.objects.create(
                user=request.user,
                email=request.user.email,
                token=token,
                expires_at=timezone.now() + timezone.timedelta(hours=1)
            )
            
            # TODO: Send email with verification link
            messages.info(request, 'Verification email sent!')
            return redirect('verify_email_2fa')
    
    context = {
        'two_factor': two_factor,
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/two_factor_setup.html', context)


@login_required
def verify_phone_2fa(request):
    """Verify phone number for 2FA."""
    if request.method == 'POST':
        code = request.POST.get('code')
        verification = PhoneVerification.objects.filter(
            user=request.user,
            code=code,
            is_verified=False
        ).first()
        
        if verification and not verification.is_expired():
            verification.is_verified = True
            verification.save()
            
            # Enable 2FA
            two_factor, created = TwoFactorAuth.objects.get_or_create(user=request.user)
            two_factor.is_enabled = True
            two_factor.method = 'sms'
            two_factor.phone_number = verification.phone_number
            two_factor.save()
            
            # Log activity
            AccountActivity.objects.create(
                user=request.user,
                activity_type='2fa_enabled',
                description='Two-factor authentication enabled via SMS',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Two-factor authentication enabled!')
            return redirect('login_security')
        else:
            messages.error(request, 'Invalid or expired verification code!')
    
    return render(request, 'accounts/settings/verify_phone_2fa.html')


@login_required
def danger_zone(request):
    """Account deactivation and deletion."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'deactivate':
            # Deactivate account
            request.user.is_active = False
            request.user.save()
            
            # Log activity
            AccountActivity.objects.create(
                user=request.user,
                activity_type='profile_updated',
                description='Account deactivated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Account deactivated successfully!')
            return redirect('logout')
        
        elif action == 'delete':
            # Delete account
            password = request.POST.get('password')
            if request.user.check_password(password):
                # Log activity before deletion
                AccountActivity.objects.create(
                    user=request.user,
                    activity_type='profile_updated',
                    description='Account deleted',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                request.user.delete()
                messages.success(request, 'Account deleted successfully!')
                return redirect('index')
            else:
                messages.error(request, 'Incorrect password!')
    
    context = {
        'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else False
    }
    
    return render(request, 'accounts/settings/danger_zone.html', context)


@login_required
@require_POST
def upload_profile_picture(request):
    """Upload profile picture via AJAX."""
    if 'profile_picture' in request.FILES:
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        
        # Delete old picture if exists
        if preferences.profile_picture:
            preferences.profile_picture.delete()
        
        # Save new picture
        preferences.profile_picture = request.FILES['profile_picture']
        preferences.save()
        
        return JsonResponse({
            'success': True,
            'url': preferences.profile_picture.url
        })
    
    return JsonResponse({'success': False, 'error': 'No file uploaded'})


@login_required
@require_POST
def delete_profile_picture(request):
    """Delete profile picture via AJAX."""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if preferences.profile_picture:
        preferences.profile_picture.delete()
        preferences.profile_picture = None
        preferences.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'No profile picture to delete'})