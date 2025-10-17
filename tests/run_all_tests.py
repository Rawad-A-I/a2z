#!/usr/bin/env python
"""
Run all tests for the Django eCommerce Website.
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def run_all_tests():
    """Run all tests."""
    print("🧪 Running all tests for Django eCommerce Website...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
    django.setup()
    
    try:
        # Run all tests
        execute_from_command_line(['manage.py', 'test', 'tests'])
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False
    
    return True

def run_specific_test(test_name):
    """Run a specific test."""
    print(f"🧪 Running {test_name} tests...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
    django.setup()
    
    try:
        # Run specific test
        execute_from_command_line(['manage.py', 'test', f'tests.{test_name}'])
        print(f"✅ {test_name} tests completed successfully!")
        
    except Exception as e:
        print(f"❌ {test_name} tests failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        run_specific_test(test_name)
    else:
        run_all_tests()
