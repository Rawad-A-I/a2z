from django.contrib import admin
from .models import Category, Product, ColorVariant, SizeVariant, ProductImage, ProductReview, ProductVariant, StockMovement

# Register your models here.

admin.site.register(Category)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'stock_quantity']
    inlines = [ProductImageAdmin]

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'price']

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name', 'price']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'size', 'color', 'stock_quantity']

# ProductBundle and BundleItem are in accounts models

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'created_at']

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductReview)