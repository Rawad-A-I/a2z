# Data migration to fix duplicate product slugs

from django.db import migrations
from django.utils.text import slugify


def fix_duplicate_slugs(apps, schema_editor):
    """Fix duplicate product slugs by making them unique"""
    Product = apps.get_model('products', 'Product')
    
    # Find products with duplicate slugs
    seen_slugs = set()
    products_to_fix = []
    
    for product in Product.objects.all():
        if product.slug in seen_slugs:
            products_to_fix.append(product)
        else:
            seen_slugs.add(product.slug)
    
    # Fix duplicate slugs
    for product in products_to_fix:
        original_slug = product.slug
        counter = 1
        new_slug = f"{original_slug}-{counter}"
        
        # Find a unique slug
        while Product.objects.filter(slug=new_slug).exists():
            counter += 1
            new_slug = f"{original_slug}-{counter}"
        
        product.slug = new_slug
        product.save()
        print(f"Fixed duplicate slug: {original_slug} -> {new_slug}")


def reverse_fix_duplicate_slugs(apps, schema_editor):
    """Reverse operation - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_product_section'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_slugs, reverse_fix_duplicate_slugs),
    ]
