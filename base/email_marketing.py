"""
Email marketing and notification system for the e-commerce platform.
"""
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import Order, Cart, Profile
from products.models import Product
import logging

logger = logging.getLogger(__name__)


def send_welcome_email(user):
    """Send welcome email to new customers."""
    try:
        subject = "Welcome to A2Z Mart! 🛒"
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/welcome_email.html', 
            {'user': user, 'site_url': settings.SITE_URL}
        )
        
        plain_message = f"""
        Welcome to A2Z Mart, {user.first_name or user.username}!
        
        Thank you for joining our community. You now have access to:
        - Exclusive deals and discounts
        - Order tracking
        - Wishlist and favorites
        - Loyalty rewards
        
        Start shopping now: {settings.SITE_URL}
        """
        
        send_mail(
            subject,
            plain_message,
            email_from,
            [user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Welcome email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")


def send_order_confirmation_email(order):
    """Send order confirmation email."""
    try:
        subject = f"Order Confirmation - {order.order_id}"
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/order_confirmation.html', 
            {'order': order, 'site_url': settings.SITE_URL}
        )
        
        plain_message = f"""
        Thank you for your order!
        
        Order ID: {order.order_id}
        Total: ${order.grand_total}
        Status: {order.status.title()}
        
        We'll notify you when your order ships.
        """
        
        send_mail(
            subject,
            plain_message,
            email_from,
            [order.user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Order confirmation sent for order {order.order_id}")
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation for {order.order_id}: {str(e)}")


def send_shipping_notification_email(order):
    """Send shipping notification email."""
    try:
        subject = f"Your Order Has Shipped - {order.order_id}"
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/shipping_notification.html', 
            {'order': order, 'site_url': settings.SITE_URL}
        )
        
        plain_message = f"""
        Great news! Your order has shipped.
        
        Order ID: {order.order_id}
        Tracking: {order.tracking_number or 'Will be provided soon'}
        
        Expected delivery: 3-5 business days
        """
        
        send_mail(
            subject,
            plain_message,
            email_from,
            [order.user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Shipping notification sent for order {order.order_id}")
        
    except Exception as e:
        logger.error(f"Failed to send shipping notification for {order.order_id}: {str(e)}")


def send_abandoned_cart_email(user, cart_items):
    """Send abandoned cart recovery email."""
    try:
        subject = "Don't forget your items! 🛒"
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/abandoned_cart.html', 
            {
                'user': user, 
                'cart_items': cart_items,
                'site_url': settings.SITE_URL
            }
        )
        
        plain_message = f"""
        Hi {user.first_name or user.username},
        
        You have items waiting in your cart:
        {chr(10).join([f"- {item.product.product_name} x{item.quantity}" for item in cart_items])}
        
        Complete your purchase now: {settings.SITE_URL}/cart/
        """
        
        send_mail(
            subject,
            plain_message,
            email_from,
            [user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Abandoned cart email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send abandoned cart email to {user.email}: {str(e)}")


def send_product_recommendation_email(user, recommended_products):
    """Send personalized product recommendations."""
    try:
        subject = "Products you might love! 💝"
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/product_recommendations.html', 
            {
                'user': user, 
                'products': recommended_products,
                'site_url': settings.SITE_URL
            }
        )
        
        plain_message = f"""
        Hi {user.first_name or user.username},
        
        Based on your preferences, we think you'll love these products:
        {chr(10).join([f"- {product.product_name} - ${product.price}" for product in recommended_products])}
        
        Shop now: {settings.SITE_URL}
        """
        
        send_mail(
            subject,
            plain_message,
            email_from,
            [user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Product recommendations sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send product recommendations to {user.email}: {str(e)}")


def send_newsletter_email(subscribers, newsletter_content):
    """Send newsletter to subscribers."""
    try:
        subject = newsletter_content.get('subject', 'A2Z Mart Newsletter')
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/newsletter.html', 
            {
                'content': newsletter_content,
                'site_url': settings.SITE_URL
            }
        )
        
        # Send to multiple recipients
        recipient_list = [subscriber.email for subscriber in subscribers]
        
        send_mail(
            subject,
            newsletter_content.get('plain_text', ''),
            email_from,
            recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Newsletter sent to {len(recipient_list)} subscribers")
        
    except Exception as e:
        logger.error(f"Failed to send newsletter: {str(e)}")


def send_low_stock_alert_email(admin_users, products):
    """Send low stock alert to administrators."""
    try:
        subject = "Low Stock Alert - Action Required"
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/low_stock_alert.html', 
            {
                'products': products,
                'site_url': settings.SITE_URL
            }
        )
        
        plain_message = f"""
        Low Stock Alert:
        {chr(10).join([f"- {product.product_name}: {product.stock_quantity} remaining" for product in products])}
        
        Please restock these items.
        """
        
        recipient_list = [admin.email for admin in admin_users]
        
        send_mail(
            subject,
            plain_message,
            email_from,
            recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Low stock alert sent to {len(recipient_list)} admins")
        
    except Exception as e:
        logger.error(f"Failed to send low stock alert: {str(e)}")


def send_promotional_email(users, promotion):
    """Send promotional email to users."""
    try:
        subject = promotion.get('subject', 'Special Offer!')
        email_from = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(
            'emails/promotional.html', 
            {
                'promotion': promotion,
                'site_url': settings.SITE_URL
            }
        )
        
        recipient_list = [user.email for user in users]
        
        send_mail(
            subject,
            promotion.get('plain_text', ''),
            email_from,
            recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Promotional email sent to {len(recipient_list)} users")
        
    except Exception as e:
        logger.error(f"Failed to send promotional email: {str(e)}")
