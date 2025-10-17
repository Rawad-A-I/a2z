#!/bin/bash

# Deployment fix script for migration conflicts and image optimization
echo "🔧 Starting deployment fix..."

# Step 1: Fix duplicate cart data
echo "📋 Step 1: Fixing duplicate cart data..."
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

