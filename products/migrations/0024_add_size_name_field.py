# Generated manually for size_name field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_add_size_variant_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='size_name',
            field=models.CharField(blank=True, help_text='Size name for this variant (e.g., Small, Medium, Large)', max_length=100),
        ),
    ]
