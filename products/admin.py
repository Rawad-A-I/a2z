from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ColorVariant, SizeVariant, ProductImage, ProductReview, ProductVariant, StockMovement, Barcode, ProductComparison, ProductRecommendation

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

class BarcodeInline(admin.TabularInline):
    model = Barcode
    extra = 1
    fields = ['barcode_value', 'barcode_type', 'is_primary', 'is_active', 'notes']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'section', 'price', 'stock_quantity', 'is_in_stock', 'created_at']
    list_filter = ['category', 'section', 'is_in_stock', 'newest_product', 'is_featured', 'is_bestseller', 'is_new_arrival', 'created_at']
    search_fields = ['product_name', 'product_desription', 'meta_title', 'keywords']
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductImageAdmin, ProductVariantInline, BarcodeInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'slug', 'category', 'product_desription', 'section')
        }),
        ('Size Variants', {
            'fields': ('parent',),
            'description': 'For size variants: select parent product. For standalone products: leave empty.'
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity', 'low_stock_threshold', 'is_in_stock')
        }),
        ('Physical Properties', {
            'fields': ('weight', 'dimensions'),
        }),
        ('Variants', {
            'fields': ('color_variant', 'size_variant'),
            'classes': ('collapse',)
        }),
        ('Marketing & SEO', {
            'fields': ('newest_product', 'is_featured', 'is_bestseller', 'is_new_arrival', 'meta_title', 'meta_description', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Product Relationships', {
            'fields': ('related_products', 'bundle_products'),
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
    list_display = ['size_name']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'size', 'color', 'stock_quantity']

# ProductBundle and BundleItem are in accounts models

@admin.register(Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    list_display = ['product', 'barcode_value', 'barcode_type', 'is_primary', 'is_active', 'created_at']
    list_filter = ['barcode_type', 'is_primary', 'is_active', 'created_at']
    search_fields = ['product__product_name', 'barcode_value', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Barcode Information', {
            'fields': ('product', 'barcode_value', 'barcode_type', 'is_primary', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'reason', 'user', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__product_name', 'reason', 'reference']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProductComparison)
class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ['user', 'products_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Products Count'

@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'score', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__product_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(ProductImage)
admin.site.register(ProductReview)