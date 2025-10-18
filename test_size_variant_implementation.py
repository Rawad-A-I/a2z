#!/usr/bin/env python
"""
Test script to verify size variant implementation
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from products.models import Product, Category
from products.forms import ProductInsertionForm

def test_model_methods():
    """Test the new model methods"""
    print("Testing model methods...")
    
    # Test has_size_variants method
    products = Product.objects.all()[:5]
    for product in products:
        has_variants = product.has_size_variants()
        display_price = product.get_display_price()
        print(f"Product: {product.product_name}")
        print(f"  Has size variants: {has_variants}")
        print(f"  Display price: {display_price}")
        print(f"  Is size variant: {product.is_size_variant}")
        print(f"  Size name: {product.size_name}")
        print()

def test_form_fields():
    """Test the form fields"""
    print("Testing form fields...")
    
    form = ProductInsertionForm()
    
    # Check if new fields exist
    if 'is_size_variant' in form.fields:
        print("✅ is_size_variant field exists")
    else:
        print("❌ is_size_variant field missing")
    
    if 'size_name' in form.fields:
        print("✅ size_name field exists")
    else:
        print("❌ size_name field missing")
    
    print(f"Form fields: {list(form.fields.keys())}")

def test_form_validation():
    """Test form validation"""
    print("Testing form validation...")
    
    # Test standalone product
    form_data = {
        'product_name': 'Test Product',
        'category': Category.objects.first().id,
        'price': 10,
        'product_desription': 'Test description',
        'is_size_variant': False,
        'size_name': '',
        'parent': '',
        'stock_quantity': 10,
        'is_in_stock': True,
    }
    
    form = ProductInsertionForm(data=form_data)
    if form.is_valid():
        print("✅ Standalone product form validation passed")
    else:
        print(f"❌ Standalone product form validation failed: {form.errors}")
    
    # Test size variant
    parent_product = Product.objects.filter(parent=None).first()
    if parent_product:
        form_data_variant = {
            'product_name': f'{parent_product.product_name} Small',
            'category': parent_product.category.id,
            'price': 15,
            'product_desription': 'Test variant description',
            'is_size_variant': True,
            'size_name': 'Small',
            'parent': parent_product.id,
            'stock_quantity': 5,
            'is_in_stock': True,
        }
        
        form_variant = ProductInsertionForm(data=form_data_variant)
        if form_variant.is_valid():
            print("✅ Size variant form validation passed")
        else:
            print(f"❌ Size variant form validation failed: {form_variant.errors}")
    else:
        print("⚠️ No parent product found for testing size variant")

if __name__ == '__main__':
    print("🧪 Testing Size Variant Implementation")
    print("=" * 50)
    
    try:
        test_model_methods()
        test_form_fields()
        test_form_validation()
        
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
