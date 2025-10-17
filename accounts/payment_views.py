"""
Payment processing views for Stripe integration.
"""
try:
    import stripe
    from django.conf import settings
    STRIPE_AVAILABLE = True
    # Set Stripe API key
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
except ImportError:
    STRIPE_AVAILABLE = False

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import json
from .models import Cart, Order, OrderItem
from .views import create_order


@login_required
def create_payment_intent(request):
    """
    Create a Stripe payment intent for the cart.
    """
    if not STRIPE_AVAILABLE:
        return JsonResponse({'error': 'Stripe not available'}, status=400)
    
    try:
        cart = get_object_or_404(Cart, user=request.user, is_paid=False)
        total_amount = cart.get_cart_total_price_after_coupon()
        
        # Convert to cents (Stripe expects amount in cents)
        amount_cents = int(total_amount * 100)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'user_id': request.user.id,
                'cart_id': str(cart.uid),
            }
        )
        
        return JsonResponse({
            'client_secret': intent.client_secret,
            'amount': amount_cents
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def process_payment(request):
    """
    Process the payment after successful Stripe payment.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')
            
            # Verify the payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Get the cart
                cart = get_object_or_404(Cart, user=request.user, is_paid=False)
                
                # Create order
                order = create_order(cart)
                order.payment_status = 'Paid'
                order.payment_mode = 'Stripe'
                order.save()
                
                # Mark cart as paid
                cart.is_paid = True
                cart.save()
                
                messages.success(request, 'Payment successful! Your order has been placed.')
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/order-details/{order.order_id}/'
                })
            else:
                return JsonResponse({'error': 'Payment not completed'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks for payment events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Handle successful payment
        handle_successful_payment(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Handle failed payment
        handle_failed_payment(payment_intent)
    
    return JsonResponse({'status': 'success'})


def handle_successful_payment(payment_intent):
    """
    Handle successful payment webhook.
    """
    # Add any additional logic for successful payments
    pass


def handle_failed_payment(payment_intent):
    """
    Handle failed payment webhook.
    """
    # Add any additional logic for failed payments
    pass


@login_required
def payment_success(request):
    """
    Display payment success page.
    """
    return render(request, 'payment_success/payment_success.html')


@login_required
def payment_cancel(request):
    """
    Display payment cancellation page.
    """
    messages.warning(request, 'Payment was cancelled. You can try again.')
    return redirect('cart')
