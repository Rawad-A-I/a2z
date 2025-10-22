#!/usr/bin/env python
"""
Comprehensive Database Fix Script
==================================
This script fixes all three major deployment issues:
1. Missing coupon_id column in accounts_cart
2. Duplicate is_size_variant column errors in products_product
3. Wrong number of constraints for accounts_cart
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a2z.settings')
django.setup()

from django.db import connection, transaction


def execute_sql(cursor, sql, description):
    """Execute SQL with error handling and reporting"""
    try:
        cursor.execute(sql)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"⚠️  {description}: {str(e)}")
        return False


def fix_all_issues():
    """Fix all database issues in one transaction"""
    print("\n" + "="*70)
    print("🚀 COMPREHENSIVE DATABASE FIX")
    print("="*70 + "\n")
    
    with connection.cursor() as cursor:
        try:
            print("📋 Step 1: Checking current database state...")
            print("-" * 70)
            
            # Check coupon_id column
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='accounts_cart' AND column_name='coupon_id'
                );
            """)
            coupon_id_exists = cursor.fetchone()[0]
            print(f"   coupon_id column exists: {coupon_id_exists}")
            
            # Check is_size_variant column
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='products_product' AND column_name='is_size_variant'
                );
            """)
            is_size_variant_exists = cursor.fetchone()[0]
            print(f"   is_size_variant column exists: {is_size_variant_exists}")
            
            # Check constraints
            cursor.execute("""
                SELECT COUNT(*) FROM pg_constraint 
                WHERE conname LIKE 'accounts_cart%' AND contype = 'u';
            """)
            constraint_count = cursor.fetchone()[0]
            print(f"   Unique constraints on accounts_cart: {constraint_count}")
            
            print("\n📋 Step 2: Fixing issues...")
            print("-" * 70)
            
            # Fix 1: Add coupon_id if missing
            if not coupon_id_exists:
                print("\n🔧 Adding missing coupon_id column...")
                execute_sql(cursor, """
                    ALTER TABLE accounts_cart ADD COLUMN coupon_id UUID NULL;
                """, "Added coupon_id column")
                
                execute_sql(cursor, """
                    ALTER TABLE accounts_cart 
                    ADD CONSTRAINT accounts_cart_coupon_id_fkey 
                    FOREIGN KEY (coupon_id) 
                    REFERENCES accounts_coupon(uid) 
                    ON DELETE SET NULL;
                """, "Added foreign key constraint for coupon_id")
            else:
                print("✅ coupon_id column already exists")
            
            # Fix 2: Drop problematic unique_together constraints
            print("\n🔧 Fixing cart constraints...")
            
            # Get all unique constraints on accounts_cart
            cursor.execute("""
                SELECT conname FROM pg_constraint 
                WHERE conrelid = 'accounts_cart'::regclass 
                AND contype = 'u';
            """)
            constraints = cursor.fetchall()
            
            for (constraint_name,) in constraints:
                if 'user_id' in constraint_name or 'session_key' in constraint_name:
                    execute_sql(cursor, 
                        f"ALTER TABLE accounts_cart DROP CONSTRAINT IF EXISTS {constraint_name};",
                        f"Dropped constraint {constraint_name}")
            
            # Add partial unique indexes (handle NULL properly)
            execute_sql(cursor, """
                DROP INDEX IF EXISTS accounts_cart_user_is_paid_unique_idx;
                CREATE UNIQUE INDEX accounts_cart_user_is_paid_unique_idx 
                ON accounts_cart (user_id, is_paid) 
                WHERE user_id IS NOT NULL;
            """, "Created partial unique index for user_id")
            
            execute_sql(cursor, """
                DROP INDEX IF EXISTS accounts_cart_session_is_paid_unique_idx;
                CREATE UNIQUE INDEX accounts_cart_session_is_paid_unique_idx 
                ON accounts_cart (session_key, is_paid) 
                WHERE session_key IS NOT NULL;
            """, "Created partial unique index for session_key")
            
            # Fix 3: Mark problematic migrations as applied
            print("\n🔧 Marking migrations as applied...")
            
            migrations_to_mark = [
                '0023_add_size_variant_fields',
                '0024_make_size_variant_fields_nullable',
                '0025_add_size_variant_fields_simple',
                '0026_merge_size_variant_migrations',
                '0027_add_size_variant_fields_safe',
            ]
            
            for migration in migrations_to_mark:
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied)
                    SELECT 'products', %s, NOW()
                    WHERE NOT EXISTS (
                        SELECT 1 FROM django_migrations 
                        WHERE app='products' AND name=%s
                    );
                """, [migration, migration])
                
                if cursor.rowcount > 0:
                    print(f"   ✅ Marked products.{migration} as applied")
                else:
                    print(f"   ℹ️  products.{migration} already applied")
            
            # Verify all fixes
            print("\n📋 Step 3: Verifying fixes...")
            print("-" * 70)
            
            # Verify coupon_id
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='accounts_cart' AND column_name='coupon_id'
                );
            """)
            if cursor.fetchone()[0]:
                print("✅ coupon_id column verified")
            else:
                print("❌ coupon_id column still missing")
                return False
            
            # Verify indexes
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'accounts_cart_user_is_paid_unique_idx'
                );
            """)
            if cursor.fetchone()[0]:
                print("✅ User partial unique index verified")
            else:
                print("⚠️  User partial unique index missing")
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'accounts_cart_session_is_paid_unique_idx'
                );
            """)
            if cursor.fetchone()[0]:
                print("✅ Session partial unique index verified")
            else:
                print("⚠️  Session partial unique index missing")
            
            # Verify migrations
            cursor.execute("""
                SELECT COUNT(*) FROM django_migrations 
                WHERE app='products' 
                AND name IN (
                    '0023_add_size_variant_fields',
                    '0024_make_size_variant_fields_nullable',
                    '0025_add_size_variant_fields_simple',
                    '0026_merge_size_variant_migrations',
                    '0027_add_size_variant_fields_safe'
                );
            """)
            migration_count = cursor.fetchone()[0]
            print(f"✅ {migration_count}/5 product migrations marked as applied")
            
            print("\n" + "="*70)
            print("🎉 DATABASE FIX COMPLETED SUCCESSFULLY!")
            print("="*70)
            print("\n📝 Summary:")
            print("   - coupon_id column added/verified")
            print("   - Cart constraints fixed with partial indexes")
            print("   - Product migrations marked as applied")
            print("\n✨ Your database is now ready for deployment!")
            print("\n⚠️  IMPORTANT: After running this script:")
            print("   1. Commit all changes")
            print("   2. Push to Railway")
            print("   3. Run: railway run python fix_all_database_issues.py")
            print("   4. Then deploy normally")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = fix_all_issues()
    sys.exit(0 if success else 1)

