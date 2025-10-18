# Generated manually to make size variant fields nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_add_size_variant_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_size_variant',
            field=models.BooleanField(blank=True, default=False, help_text='Check if this product is a size variant', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='has_size_variants',
            field=models.BooleanField(blank=True, default=False, help_text='Check if this product has different sizes', null=True),
        ),
    ]
