from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ColorVariant, SizeVariant, ProductImage, ProductReview, ProductVariant, StockMovement

# Register your models here.
#test2
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('category_name',)}
    search_fields = ['category_name']

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'section', 'price', 'stock_quantity', 'is_in_stock', 'created_at']
    list_filter = ['category', 'section', 'is_in_stock', 'newest_product', 'created_at']
    search_fields = ['product_name', 'product_desription']
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductImageAdmin, ProductVariantInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'slug', 'category', 'product_desription')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity', 'low_stock_threshold', 'is_in_stock')
        }),
        ('Variants', {
            'fields': ('color_variant', 'size_variant'),
            'classes': ('collapse',)
        }),
        ('Physical Properties', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Marketing', {
            'fields': ('newest_product', 'meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

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

admin.site.register(ProductImage)
admin.site.register(ProductReview)