from django.contrib import admin
from .models import Profile, Cart, CartItem, Order, OrderItem

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'order_date', 'payment_status']
    list_filter = ['payment_status', 'payment_mode', 'order_date']
    search_fields = ['order_id', 'user__username']
    readonly_fields = ['order_date']

admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)