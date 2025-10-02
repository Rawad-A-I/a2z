#!/usr/bin/env python
"""
Reset Database and Create Superuser
This script will clear all data and create a new superuser.
"""

import os
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection

def reset_database():
    """Reset the database and create a new superuser."""
    print("🗑️  Clearing database...")
    
    # Clear all data
    call_command('flush', '--noinput')
    print("✅ Database cleared successfully!")
    
    # Create superuser
    print("👤 Creating superuser 'rawad'...")
    
    # Check if user already exists
    if User.objects.filter(username='rawad').exists():
        print("⚠️  User 'rawad' already exists. Deleting...")
        User.objects.filter(username='rawad').delete()
    
    # Create new superuser
    User.objects.create_superuser(
        username='rawad',
        email='rawad@example.com',
        password='rawad123'
    )
    
    print("✅ Superuser 'rawad' created successfully!")
    print("📧 Email: rawad@example.com")
    print("🔑 Password: rawad123")
    
    # Create some sample data
    print("📦 Creating sample data...")
    
    # Create sample categories
    from products.models import Category
    categories = [
        'Electronics',
        'Clothing',
        'Books',
        'Home & Garden',
        'Sports'
    ]
    
    for cat_name in categories:
        Category.objects.create(category_name=cat_name)
    
    print(f"✅ Created {len(categories)} categories")
    
    # Create sample products
    from products.models import Product
    from django.utils.text import slugify
    
    sample_products = [
        {'name': 'Laptop', 'price': 999, 'category': 'Electronics'},
        {'name': 'T-Shirt', 'price': 25, 'category': 'Clothing'},
        {'name': 'Programming Book', 'price': 50, 'category': 'Books'},
        {'name': 'Garden Tools', 'price': 75, 'category': 'Home & Garden'},
        {'name': 'Running Shoes', 'price': 120, 'category': 'Sports'},
    ]
    
    for product_data in sample_products:
        category = Category.objects.get(category_name=product_data['category'])
        Product.objects.create(
            product_name=product_data['name'],
            category=category,
            price=product_data['price'],
            product_desription=f"Description for {product_data['name']}",
            stock_quantity=10
        )
    
    print(f"✅ Created {len(sample_products)} sample products")
    
    # Create sample store location
    from accounts.models import StoreLocation
    StoreLocation.objects.create(
        name='Main Store',
        address='123 Main Street',
        city='New York',
        state='NY',
        zip_code='10001',
        phone='555-0123',
        email='store@example.com',
        is_active=True
    )
    
    print("✅ Created sample store location")
    
    print("\n🎉 Database reset complete!")
    print("=" * 50)
    print("👤 Superuser: rawad")
    print("🔑 Password: rawad123")
    print("📧 Email: rawad@example.com")
    print("=" * 50)
    print("🚀 You can now start the server and login!")

if __name__ == "__main__":
    reset_database()
