# Generated manually to merge conflicting migrations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_add_size_variant_fields'),
        ('products', '0024_make_size_variant_fields_nullable'),
        ('products', '0025_add_size_variant_fields_simple'),
    ]

    operations = [
        # This is a merge migration - no operations needed
        # The conflicting migrations will be resolved by Django
    ]
