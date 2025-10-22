from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_merge_migration'),
    ]

    operations = [
        # First, ensure coupon_id column exists
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='accounts_cart' AND column_name='coupon_id'
                    ) THEN
                        ALTER TABLE accounts_cart ADD COLUMN coupon_id UUID NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="ALTER TABLE accounts_cart DROP COLUMN IF EXISTS coupon_id;"
        ),
        
        # Mark problematic migrations as applied to avoid conflicts
        migrations.RunSQL(
            sql="""
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'products', '0025_add_size_variant_fields_simple', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='products' AND name='0025_add_size_variant_fields_simple'
                );
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Mark other problematic migrations as applied
        migrations.RunSQL(
            sql="""
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'products', '0026_merge_size_variant_migrations', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='products' AND name='0026_merge_size_variant_migrations'
                );
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        migrations.RunSQL(
            sql="""
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
