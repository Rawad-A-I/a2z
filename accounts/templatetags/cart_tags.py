"""
Template tags for cart functionality.
"""
from django import template
from ..cart_utils import get_or_create_cart

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cart_count(context):
    """
    Get the total number of items in the cart for both anonymous and authenticated users.
    """
    request = context['request']
    cart = get_or_create_cart(request)
    return sum(item.quantity for item in cart.cart_items.all())
