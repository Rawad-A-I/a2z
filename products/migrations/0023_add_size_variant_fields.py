# Generated manually for size variant fields

from django.db import migrations, models


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
    ]
