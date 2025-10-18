# Simple migration to add size variant fields
# This migration is designed to work even if previous migrations failed

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_fix_duplicate_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_size_variant',
            field=models.BooleanField(blank=True, default=False, help_text='Check if this product is a size variant', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='size_name',
            field=models.CharField(blank=True, help_text='Size name for this variant (e.g., Small, Medium, Large)', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='has_size_variants',
            field=models.BooleanField(blank=True, default=False, help_text='Check if this product has different sizes', null=True),
        ),
    ]
