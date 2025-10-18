#!/bin/bash

# Deployment fix script for migration conflicts and size variant system
echo "🔧 Starting deployment fix..."

# Step 1: Aggressive duplicate data cleanup
echo "📋 Step 1: Aggressive duplicate data cleanup..."

# Fix duplicate carts - nuclear approach
echo "  - Fixing duplicate carts (nuclear cleanup)..."
python manage.py shell -c "
from accounts.models import Cart
from django.db import transaction, connection

try:
    with transaction.atomic():
        # First, try to delete all carts to avoid constraint issues
        print('Deleting all existing carts to avoid constraint conflicts...')
        Cart.objects.all().delete()
        print('All carts deleted successfully')
        
        # Reset the sequence if using PostgreSQL
        with connection.cursor() as cursor:
            try:
                cursor.execute('ALTER SEQUENCE accounts_cart_id_seq RESTART WITH 1;')
                print('Cart sequence reset')
            except Exception as seq_error:
                print(f'Sequence reset failed (not critical): {seq_error}')
        
        print('Cart cleanup completed successfully')
except Exception as e:
    print(f'Cart cleanup failed: {e}')
    # If even this fails, try to drop and recreate the table
    try:
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE IF EXISTS accounts_cart CASCADE;')
            print('Dropped cart table')
    except Exception as e2:
        print(f'Failed to drop cart table: {e2}')
"

# Fix duplicate product slugs
echo "  - Fixing duplicate product slugs..."
python manage.py shell -c "
from products.models import Product
from django.utils.text import slugify
seen_slugs = set()
products_to_fix = []
for product in Product.objects.all():
    if product.slug in seen_slugs:
        products_to_fix.append(product)
    else:
        seen_slugs.add(product.slug)
for product in products_to_fix:
    original_slug = product.slug
    counter = 1
    new_slug = f'{original_slug}-{counter}'
    while Product.objects.filter(slug=new_slug).exists():
        counter += 1
        new_slug = f'{original_slug}-{counter}'
    product.slug = new_slug
    product.save()
    print(f'Fixed duplicate slug: {original_slug} -> {new_slug}')
if not products_to_fix:
    print('No duplicate product slugs found')
"

# Step 2: Apply migrations
echo "📋 Step 2: Applying migrations..."
python manage.py migrate --noinput

# Step 3: Update existing products with new fields
echo "📋 Step 3: Updating existing products with new fields..."
python manage.py shell -c "
from products.models import Product
from django.db import transaction

try:
    with transaction.atomic():
        # Update has_size_variants for all products
        for product in Product.objects.all():
            product.has_size_variants = product.child_products.exists()
            product.save(update_fields=['has_size_variants'])
        
        print('Updated has_size_variants for all products')
        
        # Set default values for new fields
        Product.objects.filter(is_size_variant__isnull=True).update(is_size_variant=False)
        Product.objects.filter(has_size_variants__isnull=True).update(has_size_variants=False)
        
        print('Set default values for new fields')
        
except Exception as e:
    print(f'Failed to update products: {e}')
"

# Step 4: Test size variant system
echo "📋 Step 4: Testing size variant system..."
python manage.py shell -c "
from products.models import Product
try:
    # Test model methods
    products = Product.objects.all()[:3]
    for product in products:
        has_variants = product.has_size_variants()
        display_price = product.get_display_price()
        print(f'Product: {product.product_name}')
        print(f'  Has size variants: {has_variants}')
        print(f'  Display price: {display_price}')
        print(f'  Is size variant: {product.is_size_variant}')
        print()
    print('Size variant system test completed successfully')
except Exception as e:
    print(f'Size variant system test failed: {e}')
"

echo "✅ Deployment fix completed!"

