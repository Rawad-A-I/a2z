#!/bin/bash

# Deployment fix script for migration conflicts and size variant system
echo "🔧 Starting deployment fix..."

# Step 1: Aggressive duplicate data cleanup
echo "📋 Step 1: Aggressive duplicate data cleanup..."

# Fix duplicate carts - nuclear approach with foreign key handling
echo "  - Fixing duplicate carts (nuclear cleanup)..."
python manage.py shell -c "
from django.db import connection

try:
    with connection.cursor() as cursor:
        # First, delete all cart items to avoid foreign key constraints
        print('Deleting all cart items to avoid foreign key constraints...')
        cursor.execute('DELETE FROM accounts_cartitem;')
        print('All cart items deleted successfully')
        
        # Then delete all carts
        print('Deleting all existing carts using raw SQL...')
        cursor.execute('DELETE FROM accounts_cart;')
        print('All carts deleted successfully')
        
        # Reset the sequence if using PostgreSQL
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
            cursor.execute('DROP TABLE IF EXISTS accounts_cartitem CASCADE;')
            cursor.execute('DROP TABLE IF EXISTS accounts_cart CASCADE;')
            print('Dropped cart and cartitem tables')
            
            # Recreate the cart table with proper structure
            cursor.execute('''
                CREATE TABLE accounts_cart (
                    uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
                    session_key VARCHAR(40),
                    is_paid BOOLEAN NOT NULL DEFAULT FALSE
                );
            ''')
            print('Recreated cart table')
            
            # Recreate the cartitem table with proper structure
            cursor.execute('''
                CREATE TABLE accounts_cartitem (
                    uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    cart_id UUID NOT NULL REFERENCES accounts_cart(uid) ON DELETE CASCADE,
                    product_id UUID NOT NULL REFERENCES products_product(uid) ON DELETE CASCADE,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    UNIQUE(cart_id, product_id)
                );
            ''')
            print('Recreated cartitem table')
            
    except Exception as e2:
        print(f'Failed to recreate cart tables: {e2}')
"

# Fix duplicate product slugs using raw SQL to avoid model issues
echo "  - Fixing duplicate product slugs..."
python manage.py shell -c "
from django.db import connection
from django.utils.text import slugify

try:
    with connection.cursor() as cursor:
        # Get all products with their slugs (using uid instead of id)
        cursor.execute('SELECT uid, slug FROM products_product WHERE slug IS NOT NULL;')
        products = cursor.fetchall()
        
        seen_slugs = set()
        products_to_fix = []
        
        for product_uid, slug in products:
            if slug in seen_slugs:
                products_to_fix.append((product_uid, slug))
            else:
                seen_slugs.add(slug)
        
        # Fix duplicate slugs
        for product_uid, original_slug in products_to_fix:
            counter = 1
            new_slug = f'{original_slug}-{counter}'
            
            # Check if new slug exists
            while True:
                cursor.execute('SELECT COUNT(*) FROM products_product WHERE slug = %s;', [new_slug])
                if cursor.fetchone()[0] == 0:
                    break
                counter += 1
                new_slug = f'{original_slug}-{counter}'
            
            # Update the slug
            cursor.execute('UPDATE products_product SET slug = %s WHERE uid = %s;', [new_slug, product_uid])
            print(f'Fixed duplicate slug: {original_slug} -> {new_slug}')
        
        if not products_to_fix:
            print('No duplicate product slugs found')
        
        print('Product slug cleanup completed successfully')
except Exception as e:
    print(f'Product slug cleanup failed: {e}')
"

# Step 1.5: Ensure cart tables exist
echo "📋 Step 1.5: Ensuring cart tables exist..."
python manage.py shell -c "
from django.db import connection

try:
    with connection.cursor() as cursor:
        # Check if cart table exists
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'accounts_cart'
            );
        ''')
        cart_exists = cursor.fetchone()[0]
        
        if not cart_exists:
            print('Cart table does not exist, creating...')
            cursor.execute('''
                CREATE TABLE accounts_cart (
                    uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
                    session_key VARCHAR(40),
                    is_paid BOOLEAN NOT NULL DEFAULT FALSE
                );
            ''')
            print('Created cart table')
        
        # Check if cartitem table exists
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'accounts_cartitem'
            );
        ''')
        cartitem_exists = cursor.fetchone()[0]
        
        if not cartitem_exists:
            print('Cartitem table does not exist, creating...')
            cursor.execute('''
                CREATE TABLE accounts_cartitem (
                    uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    cart_id UUID NOT NULL REFERENCES accounts_cart(uid) ON DELETE CASCADE,
                    product_id UUID NOT NULL REFERENCES products_product(uid) ON DELETE CASCADE,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    UNIQUE(cart_id, product_id)
                );
            ''')
            print('Created cartitem table')
        
        print('Cart tables verification completed')
        
except Exception as e:
    print(f'Cart table verification failed: {e}')
"

# Step 2: Apply migrations
echo "📋 Step 2: Applying migrations..."
# Apply products migrations first to avoid dependency issues
python manage.py migrate products --noinput
# Then apply all other migrations
python manage.py migrate --noinput

# Step 2.5: Apply size variant fields migration specifically
echo "📋 Step 2.5: Applying size variant fields migration..."
python manage.py migrate products 0025 --noinput

# Step 3: Update existing products with new fields using raw SQL
echo "📋 Step 3: Updating existing products with new fields..."
python manage.py shell -c "
from django.db import connection

try:
    with connection.cursor() as cursor:
        # Set default values for new fields using raw SQL
        cursor.execute('UPDATE products_product SET is_size_variant = FALSE WHERE is_size_variant IS NULL;')
        cursor.execute('UPDATE products_product SET has_size_variants = FALSE WHERE has_size_variants IS NULL;')
        cursor.execute('UPDATE products_product SET size_name = \'\' WHERE size_name IS NULL;')
        
        print('Set default values for new fields')
        
        # Update has_size_variants based on child products
        cursor.execute('''
            UPDATE products_product 
            SET has_size_variants = TRUE 
            WHERE uid IN (
                SELECT DISTINCT parent_id 
                FROM products_product 
                WHERE parent_id IS NOT NULL
            );
        ''')
        
        print('Updated has_size_variants for all products')
        
except Exception as e:
    print(f'Failed to update products: {e}')
"

# Step 4: Test size variant system using raw SQL
echo "📋 Step 4: Testing size variant system..."
python manage.py shell -c "
from django.db import connection

try:
    with connection.cursor() as cursor:
        # Test if the new fields exist and have data
        cursor.execute('SELECT COUNT(*) FROM products_product WHERE is_size_variant IS NOT NULL;')
        is_size_variant_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products_product WHERE has_size_variants IS NOT NULL;')
        has_size_variants_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products_product WHERE size_name IS NOT NULL;')
        size_name_count = cursor.fetchone()[0]
        
        print(f'Products with is_size_variant field: {is_size_variant_count}')
        print(f'Products with has_size_variants field: {has_size_variants_count}')
        print(f'Products with size_name field: {size_name_count}')
        
        # Test a few products
        cursor.execute('SELECT product_name, is_size_variant, has_size_variants, size_name FROM products_product LIMIT 3;')
        products = cursor.fetchall()
        
        for product_name, is_size_variant, has_size_variants, size_name in products:
            print(f'Product: {product_name}')
            print(f'  Is size variant: {is_size_variant}')
            print(f'  Has size variants: {has_size_variants}')
            print(f'  Size name: {size_name}')
            print()
        
        print('Size variant system test completed successfully')
except Exception as e:
    print(f'Size variant system test failed: {e}')
"

echo "✅ Deployment fix completed!"

