#!/usr/bin/env python
"""
Direct fix for the missing coupon_id column.
This script will add the missing column to your database.
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


def fix_coupon_id_column():
    """Add the missing coupon_id column to accounts_cart table."""
    print("🚨 FIXING MISSING COUPON_ID COLUMN...")
    
    try:
        with connection.cursor() as cursor:
            # Check if column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='accounts_cart' AND column_name='coupon_id'
            """)
            
            if cursor.fetchone():
                print("✅ coupon_id column already exists")
                return True
            
            # Add the missing column
            print("📋 Adding missing coupon_id column...")
            cursor.execute("""
                ALTER TABLE accounts_cart 
                ADD COLUMN coupon_id UUID NULL
            """)
            
            print("✅ Successfully added coupon_id column to accounts_cart table")
            return True
            
    except Exception as e:
        print(f"❌ Error adding coupon_id column: {e}")
        return False


def verify_fix():
    """Verify that the fix worked."""
    print("🔍 Verifying fix...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='accounts_cart' AND column_name='coupon_id'
            """)
            
            if cursor.fetchone():
                print("✅ VERIFICATION SUCCESSFUL: coupon_id column exists")
                return True
            else:
                print("❌ VERIFICATION FAILED: coupon_id column still missing")
                return False
                
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def main():
    """Main fix function."""
    print("🚨 STARTING COUPON_ID COLUMN FIX...")
    print("=" * 50)
    
    # Step 1: Fix the column
    if not fix_coupon_id_column():
        print("❌ Fix failed. Exiting.")
        return False
    
    # Step 2: Verify the fix
    if not verify_fix():
        print("❌ Verification failed. Exiting.")
        return False
    
    print("\n🎉 COUPON_ID COLUMN FIX COMPLETED SUCCESSFULLY!")
    print("\n📝 Summary:")
    print("✅ Added missing coupon_id column to accounts_cart table")
    print("✅ Fix verified successfully")
    
    print("\n🎯 Next steps:")
    print("1. Your deployment should now work without errors")
    print("2. Test your application to ensure it's working")
    print("3. The coupon_id column is now available for your Cart model")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
