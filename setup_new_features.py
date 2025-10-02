#!/usr/bin/env python
"""
Setup script for new eCommerce features.
Run this script to set up the new features.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_new_features():
    """Set up the new eCommerce features."""
    print("🚀 Setting up new eCommerce features...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings_simple')
    django.setup()
    
    try:
        # Create migrations
        print("📝 Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Apply migrations
        print("🗄️ Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Create superuser if it doesn't exist
        print("👤 Creating superuser...")
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("Please create a superuser:")
            execute_from_command_line(['manage.py', 'createsuperuser'])
        
        # Create sample data
        print("📊 Creating sample data...")
        create_sample_data()
        
        print("✅ Setup complete! Your eCommerce system is ready.")
        print("\n🎯 Next steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://localhost:8000")
        print("3. Login as superuser to access admin features")
        print("4. Configure store locations in admin panel")
        print("5. Set up inventory alerts for low stock")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False
    
    return True

def create_sample_data():
    """Create sample data for testing."""
    from accounts.models import StoreLocation, CustomerLoyalty
    from products.models import Category, Product
    from django.contrib.auth.models import User
    
    # Create sample store location
    if not StoreLocation.objects.exists():
        StoreLocation.objects.create(
            name="Main Store",
            address="123 Main Street",
            city="New York",
            state="NY",
            zip_code="10001",
            phone="(555) 123-4567",
            email="info@store.com",
            latitude=40.7128,
            longitude=-74.0060
        )
        print("✅ Created sample store location")
    
    # Create sample category if it doesn't exist
    if not Category.objects.exists():
        Category.objects.create(
            category_name="Electronics",
            category_image="catgories/electronics.jpg"
        )
        print("✅ Created sample category")
    
    # Create sample product if it doesn't exist
    if not Product.objects.exists():
        category = Category.objects.first()
        if category:
            Product.objects.create(
                product_name="Sample Product",
                category=category,
                price=99.99,
                product_desription="A sample product for testing",
                stock_quantity=100,
                low_stock_threshold=10
            )
            print("✅ Created sample product")

if __name__ == '__main__':
    setup_new_features()
