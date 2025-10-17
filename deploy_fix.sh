#!/bin/bash

# Deployment fix script for migration conflicts and image optimization
echo "🔧 Starting deployment fix..."

# Step 1: Fix duplicate data issues
echo "📋 Step 1: Fixing duplicate data issues..."

# Fix duplicate carts
echo "  - Fixing duplicate carts..."
python manage.py shell -c "
from accounts.models import Cart
seen = set()
duplicates = []
for cart in Cart.objects.all():
    key = (cart.user_id, cart.is_paid)
    if key in seen:
        duplicates.append(cart.id)
    else:
        seen.add(key)
if duplicates:
    Cart.objects.filter(id__in=duplicates).delete()
    print(f'Removed {len(duplicates)} duplicate carts')
else:
    print('No duplicate carts found')
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

