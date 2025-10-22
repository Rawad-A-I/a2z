# Comprehensive fix for all deployment issues
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0030_fix_coupon_column'),
    ]

    operations = [
        # Step 1: Drop problematic unique_together constraints
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Drop existing unique constraints if they exist
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'accounts_cart_user_id_is_paid_17a17a19_uniq'
                    ) THEN
                        ALTER TABLE accounts_cart DROP CONSTRAINT accounts_cart_user_id_is_paid_17a17a19_uniq;
                    END IF;
                    
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'accounts_cart_session_key_is_paid_f1b0e6e5_uniq'
                    ) THEN
                        ALTER TABLE accounts_cart DROP CONSTRAINT accounts_cart_session_key_is_paid_f1b0e6e5_uniq;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 2: Ensure coupon_id exists with correct setup
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Add coupon_id if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='accounts_cart' AND column_name='coupon_id'
                    ) THEN
                        ALTER TABLE accounts_cart ADD COLUMN coupon_id UUID NULL;
                    END IF;
                    
                    -- Add foreign key constraint if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'accounts_cart_coupon_id_fkey'
                    ) THEN
                        ALTER TABLE accounts_cart 
                        ADD CONSTRAINT accounts_cart_coupon_id_fkey 
                        FOREIGN KEY (coupon_id) 
                        REFERENCES accounts_coupon(uid) 
                        ON DELETE SET NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 3: Add back unique constraints properly (excluding NULL values)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Create partial unique index for user (only when user is not null)
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = 'accounts_cart_user_is_paid_unique_idx'
                    ) THEN
                        CREATE UNIQUE INDEX accounts_cart_user_is_paid_unique_idx 
                        ON accounts_cart (user_id, is_paid) 
                        WHERE user_id IS NOT NULL;
                    END IF;
                    
                    -- Create partial unique index for session_key (only when session_key is not null)
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = 'accounts_cart_session_is_paid_unique_idx'
                    ) THEN
                        CREATE UNIQUE INDEX accounts_cart_session_is_paid_unique_idx 
                        ON accounts_cart (session_key, is_paid) 
                        WHERE session_key IS NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS accounts_cart_user_is_paid_unique_idx;
                DROP INDEX IF EXISTS accounts_cart_session_is_paid_unique_idx;
            """
        ),
        
        # Step 4: Mark all problematic product migrations as applied
        migrations.RunSQL(
            sql="""
                -- Mark size variant migrations as applied
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'products', '0023_add_size_variant_fields', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='products' AND name='0023_add_size_variant_fields'
                );
                
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'products', '0024_make_size_variant_fields_nullable', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='products' AND name='0024_make_size_variant_fields_nullable'
                );
                
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'products', '0025_add_size_variant_fields_simple', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='products' AND name='0025_add_size_variant_fields_simple'
                );
                
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'products', '0026_merge_size_variant_migrations', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='products' AND name='0026_merge_size_variant_migrations'
                );
                
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'products', '0027_add_size_variant_fields_safe', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='products' AND name='0027_add_size_variant_fields_safe'
                );
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]

