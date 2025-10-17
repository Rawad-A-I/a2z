"""
Image optimization utilities for product images
Handles automatic resizing, compression, and format conversion
"""
import os
import uuid
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import io


class ImageOptimizer:
    """Handles image optimization for product images"""
    
    # Minimum dimensions for different image types
    MIN_DIMENSIONS = {
        'product_primary': (400, 400),      # Minimum for primary product images
        'product_thumbnail': (200, 200),    # Minimum for thumbnails
        'product_gallery': (300, 300),      # Minimum for gallery images
        'category': (300, 300),             # Minimum for category images
    }
    
    # Optimal dimensions for different image types
    OPTIMAL_DIMENSIONS = {
        'product_primary': (800, 800),      # Optimal for primary product images
        'product_thumbnail': (400, 400),    # Optimal for thumbnails
        'product_gallery': (600, 600),      # Optimal for gallery images
        'category': (500, 500),             # Optimal for category images
    }
    
    # Quality settings for different formats
    QUALITY_SETTINGS = {
        'JPEG': 85,
        'WEBP': 80,
        'AVIF': 75,
    }
    
    @classmethod
    def get_available_formats(cls):
        """Get list of available image formats"""
        available_formats = ['JPEG', 'WEBP']
        
        # Check if AVIF is available
        try:
            from PIL import Image
            # Try to create a small AVIF image to test support
            test_img = Image.new('RGB', (1, 1), (255, 255, 255))
            test_img.save('/tmp/test.avif', format='AVIF')
            available_formats.append('AVIF')
        except:
            pass  # AVIF not available
        
        return available_formats
    
    @classmethod
    def optimize_image(cls, image_file, image_type='product_primary', target_format='WEBP'):
        """
        Optimize an image file for web use
        
        Args:
            image_file: Django uploaded file or PIL Image
            image_type: Type of image (product_primary, product_thumbnail, etc.)
            target_format: Target format (JPEG, WEBP, AVIF)
            
        Returns:
            Optimized image as ContentFile
        """
        try:
            # Open image
            if hasattr(image_file, 'read'):
                # Django uploaded file
                image = Image.open(image_file)
            else:
                # PIL Image
                image = image_file
            
            # Convert to RGB if necessary (for JPEG/WebP)
            if target_format in ['JPEG', 'WEBP'] and image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif target_format == 'AVIF' and image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get target dimensions
            min_width, min_height = cls.MIN_DIMENSIONS.get(image_type, (400, 400))
            optimal_width, optimal_height = cls.OPTIMAL_DIMENSIONS.get(image_type, (800, 800))
            
            # Resize image if needed
            image = cls._resize_image(image, min_width, min_height, optimal_width, optimal_height)
            
            # Apply image enhancements
            image = cls._enhance_image(image)
            
            # Convert to target format with fallback
            output = io.BytesIO()
            quality = cls.QUALITY_SETTINGS.get(target_format, 85)
            available_formats = cls.get_available_formats()
            
            # Try target format, fallback to available formats
            format_priority = [target_format, 'WEBP', 'JPEG']
            successful_format = None
            
            for fmt in format_priority:
                if fmt in available_formats:
                    try:
                        if fmt == 'JPEG':
                            image.save(output, format='JPEG', quality=quality, optimize=True)
                        elif fmt == 'WEBP':
                            image.save(output, format='WEBP', quality=quality, optimize=True)
                        elif fmt == 'AVIF':
                            image.save(output, format='AVIF', quality=quality, optimize=True)
                        successful_format = fmt
                        break
                    except Exception as e:
                        print(f"Failed to save as {fmt}: {e}")
                        continue
            
            # Final fallback to JPEG
            if not successful_format:
                image.save(output, format='JPEG', quality=85, optimize=True)
                successful_format = 'JPEG'
            
            output.seek(0)
            
            # Generate filename with actual format used
            filename = cls._generate_filename(successful_format)
            
            return ContentFile(output.getvalue(), name=filename)
            
        except Exception as e:
            print(f"Error optimizing image: {e}")
            # Return original file if optimization fails
            return image_file
    
    @classmethod
    def _resize_image(cls, image, min_width, min_height, optimal_width, optimal_height):
        """Resize image while maintaining aspect ratio"""
        original_width, original_height = image.size
        
        # If image is smaller than minimum, upscale
        if original_width < min_width or original_height < min_height:
            # Calculate scale factor to meet minimum dimensions
            scale_x = min_width / original_width
            scale_y = min_height / original_height
            scale = max(scale_x, scale_y)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # If image is larger than optimal, downscale
        elif original_width > optimal_width or original_height > optimal_height:
            # Calculate scale factor to fit optimal dimensions
            scale_x = optimal_width / original_width
            scale_y = optimal_height / original_height
            scale = min(scale_x, scale_y)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    @classmethod
    def _enhance_image(cls, image):
        """Apply image enhancements"""
        # Auto-orient based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Enhance contrast and sharpness slightly
        from PIL import ImageEnhance
        
        # Slight contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # Slight sharpness enhancement
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    @classmethod
    def _generate_filename(cls, format):
        """Generate unique filename with proper extension"""
        unique_id = str(uuid.uuid4())[:8]
        extension = format.lower()
        if extension == 'jpeg':
            extension = 'jpg'
        return f"optimized_{unique_id}.{extension}"
    
    @classmethod
    def create_multiple_sizes(cls, image_file, image_type='product_primary'):
        """
        Create multiple sizes of an image for responsive design
        
        Returns:
            Dictionary with different sizes
        """
        sizes = {
            'thumbnail': (200, 200),
            'medium': (400, 400),
            'large': (800, 800),
            'xlarge': (1200, 1200),
        }
        
        optimized_images = {}
        
        for size_name, dimensions in sizes.items():
            try:
                # Open original image
                if hasattr(image_file, 'read'):
                    image = Image.open(image_file)
                else:
                    image = image_file
                
                # Resize to specific dimensions
                image = image.resize(dimensions, Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                
                # Save with format fallback
                output = io.BytesIO()
                available_formats = cls.get_available_formats()
                
                # Try WebP first, fallback to JPEG
                if 'WEBP' in available_formats:
                    try:
                        image.save(output, format='WEBP', quality=80, optimize=True)
                        extension = 'webp'
                    except:
                        image.save(output, format='JPEG', quality=85, optimize=True)
                        extension = 'jpg'
                else:
                    image.save(output, format='JPEG', quality=85, optimize=True)
                    extension = 'jpg'
                
                output.seek(0)
                
                filename = f"{size_name}_{str(uuid.uuid4())[:8]}.{extension}"
                optimized_images[size_name] = ContentFile(output.getvalue(), name=filename)
                
            except Exception as e:
                print(f"Error creating {size_name} size: {e}")
                continue
        
        return optimized_images
    
    @classmethod
    def validate_image(cls, image_file):
        """
        Validate image file before processing
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size (max 10MB)
            if hasattr(image_file, 'size') and image_file.size > 10 * 1024 * 1024:
                return False, "Image file is too large. Maximum size is 10MB."
            
            # Check file format
            if hasattr(image_file, 'name'):
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif', '.bmp']
                file_extension = os.path.splitext(image_file.name)[1].lower()
                if file_extension not in allowed_extensions:
                    return False, f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            
            # Try to open image
            if hasattr(image_file, 'read'):
                image = Image.open(image_file)
            else:
                image = image_file
            
            # Check image dimensions
            width, height = image.size
            if width < 100 or height < 100:
                return False, "Image dimensions are too small. Minimum size is 100x100 pixels."
            
            if width > 5000 or height > 5000:
                return False, "Image dimensions are too large. Maximum size is 5000x5000 pixels."
            
            return True, "Image is valid"
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"


def optimize_product_image(image_file, is_primary=False):
    """
    Convenience function for optimizing product images
    
    Args:
        image_file: Django uploaded file
        is_primary: Whether this is a primary product image
        
    Returns:
        Optimized image as ContentFile
    """
    image_type = 'product_primary' if is_primary else 'product_gallery'
    return ImageOptimizer.optimize_image(image_file, image_type, 'WEBP')


def optimize_category_image(image_file):
    """
    Convenience function for optimizing category images
    
    Args:
        image_file: Django uploaded file
        
    Returns:
        Optimized image as ContentFile
    """
    return ImageOptimizer.optimize_image(image_file, 'category', 'WEBP')
