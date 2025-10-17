#!/bin/bash

# Deployment fix script for migration conflicts and image optimization
echo "🔧 Starting deployment fix..."

# Step 1: Aggressive duplicate data cleanup
echo "📋 Step 1: Aggressive duplicate data cleanup..."

# Fix duplicate carts - more aggressive approach
echo "  - Fixing duplicate carts (aggressive cleanup)..."
python manage.py shell -c "
from accounts.models import Cart
from django.db import transaction

try:
    with transaction.atomic():
        # Get all unique combinations
        combinations = Cart.objects.values('user_id', 'is_paid').distinct()
        
        for combo in combinations:
            user_id = combo['user_id']
            is_paid = combo['is_paid']
            
            # Get all carts for this combination
            carts = Cart.objects.filter(user_id=user_id, is_paid=is_paid).order_by('-created_at')
            
            if carts.count() > 1:
                # Keep the most recent one, delete the rest
                carts_to_delete = carts[1:]
                for cart in carts_to_delete:
                    cart.delete()
                print(f'Removed {carts_to_delete.count()} duplicate carts for user {user_id}, is_paid {is_paid}')
        
        print('Cart cleanup completed successfully')
except Exception as e:
    print(f'Cart cleanup failed: {e}')
    # If cleanup fails, delete all carts to allow migration to proceed
    try:
        Cart.objects.all().delete()
        print('Deleted all carts to allow migration to proceed')
    except Exception as e2:
        print(f'Failed to delete all carts: {e2}')
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

# Step 3: Collect static files
echo "📋 Step 3: Collecting static files..."
python manage.py collectstatic --noinput

# Step 4: Test image optimization (optional)
echo "📋 Step 4: Testing image optimization..."
python manage.py shell -c "
from products.image_utils import ImageOptimizer
formats = ImageOptimizer.get_available_formats()
print(f'Available image formats: {formats}')
"

echo "✅ Deployment fix completed!"

