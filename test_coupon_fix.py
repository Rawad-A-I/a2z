#!/usr/bin/env python
"""
Test script to verify the coupon_id column fix.
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line


def test_coupon_column():
    """Test if the coupon_id column exists."""
    print("🔍 Testing coupon_id column...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='accounts_cart' AND column_name='coupon_id'
            """)
            
            result = cursor.fetchone()
            if result:
                print("✅ coupon_id column exists")
                return True
            else:
                print("❌ coupon_id column missing")
                return False
                
    except Exception as e:
        print(f"❌ Error checking column: {e}")
        return False


def apply_migration():
    """Apply the new migration."""
    print("📋 Applying migration...")
    
    try:
        execute_from_command_line(['manage.py', 'migrate', 'accounts', '0030_fix_coupon_column'])
        print("✅ Migration applied successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚨 TESTING COUPON_ID FIX...")
    print("=" * 50)
    
    # Step 1: Check current state
    print("Step 1: Checking current state...")
    column_exists = test_coupon_column()
    
    if not column_exists:
        print("Step 2: Applying migration...")
        if apply_migration():
            print("Step 3: Verifying fix...")
            if test_coupon_column():
                print("\n🎉 COUPON_ID FIX SUCCESSFUL!")
                print("✅ Migration applied")
                print("✅ Column exists")
                print("✅ Deployment should now work")
                return True
            else:
                print("\n❌ Fix verification failed")
                return False
        else:
            print("\n❌ Migration failed")
            return False
    else:
        print("\n✅ Column already exists - no fix needed")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
