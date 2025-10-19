# Generated manually for safe size variant fields addition

from django.db import migrations, models, connection


def check_column_exists(table_name, column_name):
    """Check if a column exists in the table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            );
        """, [table_name, column_name])
        return cursor.fetchone()[0]


def add_fields_if_not_exist(apps, schema_editor):
    """Add fields only if they don't exist"""
    with connection.cursor() as cursor:
        # Check and add is_size_variant field
        if not check_column_exists('products_product', 'is_size_variant'):
            cursor.execute('ALTER TABLE products_product ADD COLUMN is_size_variant BOOLEAN DEFAULT FALSE;')
            print('Added is_size_variant field')
        else:
            print('is_size_variant field already exists')
        
        # Check and add size_name field
        if not check_column_exists('products_product', 'size_name'):
            cursor.execute('ALTER TABLE products_product ADD COLUMN size_name VARCHAR(100) DEFAULT \'\';')
            print('Added size_name field')
        else:
            print('size_name field already exists')
        
        # Check and add has_size_variants field
        if not check_column_exists('products_product', 'has_size_variants'):
            cursor.execute('ALTER TABLE products_product ADD COLUMN has_size_variants BOOLEAN DEFAULT FALSE;')
            print('Added has_size_variants field')
        else:
            print('has_size_variants field already exists')


def remove_fields_if_exist(apps, schema_editor):
    """Remove fields if they exist (reverse migration)"""
    with connection.cursor() as cursor:
        if check_column_exists('products_product', 'is_size_variant'):
            cursor.execute('ALTER TABLE products_product DROP COLUMN is_size_variant;')
        if check_column_exists('products_product', 'size_name'):
            cursor.execute('ALTER TABLE products_product DROP COLUMN size_name;')
        if check_column_exists('products_product', 'has_size_variants'):
            cursor.execute('ALTER TABLE products_product DROP COLUMN has_size_variants;')


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_fix_duplicate_slugs'),
    ]

    operations = [
        migrations.RunPython(add_fields_if_not_exist, remove_fields_if_exist),
    ]
