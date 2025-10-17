"""
Management command to create default color and size variants.
"""
from django.core.management.base import BaseCommand
from products.models import ColorVariant, SizeVariant


class Command(BaseCommand):
    help = 'Create default color and size variants for products'

    def handle(self, *args, **options):
        # Default colors
        default_colors = [
            'Red', 'Blue', 'Green', 'Yellow', 'Black', 'White', 
            'Gray', 'Brown', 'Pink', 'Purple', 'Orange', 'Navy'
        ]
        
        # Default sizes
        default_sizes = [
            'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL',
            'Small', 'Medium', 'Large', 'Extra Large',
            '28', '30', '32', '34', '36', '38', '40', '42', '44', '46'
        ]
        
        # Create color variants
        colors_created = 0
        for color_name in default_colors:
            color, created = ColorVariant.objects.get_or_create(
                color_name=color_name,
                defaults={'price': 0}
            )
            if created:
                colors_created += 1
                self.stdout.write(f'Created color variant: {color_name}')
        
        # Create size variants
        sizes_created = 0
        for size_name in default_sizes:
            size, created = SizeVariant.objects.get_or_create(
                size_name=size_name,
                defaults={'price': 0}
            )
            if created:
                sizes_created += 1
                self.stdout.write(f'Created size variant: {size_name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {colors_created} color variants and {sizes_created} size variants'
            )
        )

