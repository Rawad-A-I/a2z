# Generated manually for size variant fields

from django.db import migrations, models


def update_has_size_variants(apps, schema_editor):
    """Update has_size_variants field for existing products"""
    Product = apps.get_model('products', 'Product')
    
    for product in Product.objects.all():
        # Check if product has child products
        has_variants = product.child_products.exists()
        product.has_size_variants = has_variants
        product.save(update_fields=['has_size_variants'])


def reverse_update_has_size_variants(apps, schema_editor):
    """Reverse operation - no need to do anything"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_fix_duplicate_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_size_variant',
            field=models.BooleanField(default=False, help_text='Check if this product is a size variant'),
        ),
        migrations.AddField(
            model_name='product',
            name='size_name',
            field=models.CharField(blank=True, help_text='Size name for this variant (e.g., Small, Medium, Large)', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='has_size_variants',
            field=models.BooleanField(default=False, help_text='Check if this product has different sizes'),
        ),
        migrations.RunPython(
            update_has_size_variants,
            reverse_update_has_size_variants,
        ),
    ]
