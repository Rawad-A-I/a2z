"""
Simple test script to verify image optimization works
Run this to test the image optimization system
"""
import os
import sys
import django
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from products.image_utils import ImageOptimizer

def test_image_optimization():
    """Test the image optimization system"""
    print("🧪 Testing Image Optimization System")
    print("=" * 50)
    
    # Test 1: Check available formats
    print("\n1. Checking available formats...")
    available_formats = ImageOptimizer.get_available_formats()
    print(f"   Available formats: {', '.join(available_formats)}")
    
    # Test 2: Create a test image
    print("\n2. Creating test image...")
    test_image = Image.new('RGB', (1000, 1000), (255, 0, 0))  # Red square
    test_buffer = io.BytesIO()
    test_image.save(test_buffer, format='JPEG', quality=95)
    test_buffer.seek(0)
    
    # Create a mock file object
    class MockFile:
        def __init__(self, buffer):
            self.buffer = buffer
            self.size = len(buffer.getvalue())
        
        def read(self):
            return self.buffer.getvalue()
    
    mock_file = MockFile(test_buffer)
    print(f"   Original size: {mock_file.size} bytes")
    
    # Test 3: Optimize the image
    print("\n3. Optimizing image...")
    try:
        optimized = ImageOptimizer.optimize_image(mock_file, 'product_primary', 'WEBP')
        print(f"   Optimized size: {len(optimized.read())} bytes")
        
        # Calculate savings
        original_size = mock_file.size
        optimized_size = len(optimized.read())
        savings = original_size - optimized_size
        savings_percent = (savings / original_size) * 100
        
        print(f"   Savings: {savings} bytes ({savings_percent:.1f}%)")
        print("   ✅ Optimization successful!")
        
    except Exception as e:
        print(f"   ❌ Optimization failed: {e}")
        return False
    
    # Test 4: Test validation
    print("\n4. Testing image validation...")
    is_valid, message = ImageOptimizer.validate_image(mock_file)
    print(f"   Validation result: {is_valid}")
    print(f"   Message: {message}")
    
    # Test 5: Test with different formats
    print("\n5. Testing format fallbacks...")
    for format_name in ['WEBP', 'JPEG', 'AVIF']:
        try:
            test_buffer.seek(0)
            mock_file = MockFile(test_buffer)
            optimized = ImageOptimizer.optimize_image(mock_file, 'product_primary', format_name)
            print(f"   {format_name}: ✅ Success")
        except Exception as e:
            print(f"   {format_name}: ❌ Failed - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Image optimization system test completed!")
    return True

if __name__ == "__main__":
    test_image_optimization()
