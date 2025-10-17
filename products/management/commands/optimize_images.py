"""
Django management command to optimize existing images
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from products.models import ProductImage, Category
from products.image_utils import ImageOptimizer
import os


class Command(BaseCommand):
    help = 'Optimize existing product and category images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of already optimized images',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Optimize only images for a specific category',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        category_filter = options.get('category')

        self.stdout.write(
            self.style.SUCCESS('Starting image optimization process...')
        )

        # Optimize product images
        self.optimize_product_images(dry_run, force, category_filter)
        
        # Optimize category images
        self.optimize_category_images(dry_run, force)

        self.stdout.write(
            self.style.SUCCESS('Image optimization process completed!')
        )

    def optimize_product_images(self, dry_run, force, category_filter):
        """Optimize product images"""
        self.stdout.write('\n--- Optimizing Product Images ---')
        
        # Build query
        query = ProductImage.objects.all()
        if category_filter:
            query = query.filter(product__category__category_name__icontains=category_filter)
        
        if not force:
            # Skip already optimized images
            query = query.filter(optimized_size__isnull=True)
        
        total_images = query.count()
        self.stdout.write(f'Found {total_images} product images to optimize')
        
        if total_images == 0:
            self.stdout.write('No product images to optimize')
            return
        
        optimized_count = 0
        error_count = 0
        
        for i, product_image in enumerate(query, 1):
            try:
                self.stdout.write(f'Processing {i}/{total_images}: {product_image.product.product_name}')
                
                if not dry_run:
                    # Check if image file exists
                    if not product_image.image or not os.path.exists(product_image.image.path):
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️  Image file not found: {product_image.image}')
                        )
                        error_count += 1
                        continue
                    
                    # Optimize image
                    with transaction.atomic():
                        # Re-save to trigger optimization
                        product_image.save()
                    
                    # Get optimization info
                    info = product_image.get_optimization_info()
                    if info:
                        self.stdout.write(
                            f'  ✅ Optimized: {info["original_size"]} → {info["optimized_size"]} bytes '
                            f'({info["savings_percent"]}% savings)'
                        )
                    else:
                        self.stdout.write('  ✅ Optimized (no size info available)')
                    
                    optimized_count += 1
                else:
                    self.stdout.write(f'  🔍 Would optimize: {product_image.image}')
                    optimized_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error optimizing {product_image.product.product_name}: {e}')
                )
                error_count += 1
        
        self.stdout.write(f'\nProduct Images Summary:')
        self.stdout.write(f'  Optimized: {optimized_count}')
        self.stdout.write(f'  Errors: {error_count}')
        self.stdout.write(f'  Total: {total_images}')

    def optimize_category_images(self, dry_run, force):
        """Optimize category images"""
        self.stdout.write('\n--- Optimizing Category Images ---')
        
        # Build query
        query = Category.objects.all()
        if not force:
            # Skip already optimized images
            query = query.filter(optimized_size__isnull=True)
        
        total_categories = query.count()
        self.stdout.write(f'Found {total_categories} category images to optimize')
        
        if total_categories == 0:
            self.stdout.write('No category images to optimize')
            return
        
        optimized_count = 0
        error_count = 0
        
        for i, category in enumerate(query, 1):
            try:
                self.stdout.write(f'Processing {i}/{total_categories}: {category.category_name}')
                
                if not dry_run:
                    # Check if image file exists
                    if not category.category_image or not os.path.exists(category.category_image.path):
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️  Image file not found: {category.category_image}')
                        )
                        error_count += 1
                        continue
                    
                    # Optimize image
                    with transaction.atomic():
                        # Re-save to trigger optimization
                        category.save()
                    
                    # Get optimization info
                    info = category.get_optimization_info()
                    if info:
                        self.stdout.write(
                            f'  ✅ Optimized: {info["original_size"]} → {info["optimized_size"]} bytes '
                            f'({info["savings_percent"]}% savings)'
                        )
                    else:
                        self.stdout.write('  ✅ Optimized (no size info available)')
                    
                    optimized_count += 1
                else:
                    self.stdout.write(f'  🔍 Would optimize: {category.category_image}')
                    optimized_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error optimizing {category.category_name}: {e}')
                )
                error_count += 1
        
        self.stdout.write(f'\nCategory Images Summary:')
        self.stdout.write(f'  Optimized: {optimized_count}')
        self.stdout.write(f'  Errors: {error_count}')
        self.stdout.write(f'  Total: {total_categories}')

    def get_file_size(self, file_path):
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
