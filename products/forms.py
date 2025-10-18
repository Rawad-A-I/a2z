from django import forms
from .models import Product, Category, Barcode, ColorVariant, SizeVariant, ProductReview, ProductImage
from django.contrib.auth.models import User


class BarcodeForm(forms.ModelForm):
    """Form for adding barcodes to products"""
    class Meta:
        model = Barcode
        fields = ['barcode_value', 'barcode_type', 'is_primary', 'notes']
        widgets = {
            'barcode_value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter barcode value'
            }),
            'barcode_type': forms.Select(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this barcode'
            })
        }
    
    def clean_barcode_value(self):
        barcode_value = self.cleaned_data.get('barcode_value')
        
        if barcode_value:
            # Check if barcode already exists
            existing = Barcode.objects.filter(barcode_value=barcode_value)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f"Barcode '{barcode_value}' already exists for another product."
                )
        
        return barcode_value


class ProductInsertionForm(forms.ModelForm):
    """Form for employees to insert new products with all characteristics"""
    
    # New fields for size variant system
    is_size_variant = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Check if this is a size variant of an existing product"
    )
    size_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Small, Medium, Large, Regular'
        }),
        help_text="Size name for this variant (e.g., Small, Medium, Large)"
    )
    
    class Meta:
        model = Product
        fields = [
            'product_name', 'category', 'price', 'product_desription',
            'parent', 'color_variant', 'size_variant', 'newest_product',
            'is_in_stock', 'stock_quantity', 'low_stock_threshold',
            'weight', 'dimensions', 'section', 'is_featured', 
            'is_bestseller', 'is_new_arrival', 'meta_title', 
            'meta_description', 'keywords', 'related_products', 'bundle_products'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'product_desription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select parent product (optional)'
            }),
            'color_variant': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'size_variant': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'newest_product': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '10'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Weight in kg'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10x5x3 cm'
            }),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_bestseller': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'SEO description'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comma-separated keywords'
            }),
            'related_products': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'bundle_products': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.fields['is_in_stock'].initial = True
        self.fields['stock_quantity'].initial = 0
        self.fields['low_stock_threshold'].initial = 10
        
        # Set up querysets for related fields
        self.fields['parent'].queryset = Product.objects.filter(parent=None)  # Only parent products
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = "Select parent product (for size variants only)"
        
        self.fields['related_products'].queryset = Product.objects.all()
        self.fields['related_products'].required = False
        
        self.fields['bundle_products'].queryset = Product.objects.all()
        self.fields['bundle_products'].required = False
        
        # Make price optional initially - will be validated in clean method
        self.fields['price'].required = False
        
        # Make variant fields optional
        self.fields['color_variant'].required = False
        self.fields['size_variant'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        parent = cleaned_data.get('parent')
        is_size_variant = cleaned_data.get('is_size_variant')
        size_name = cleaned_data.get('size_name')
        price = cleaned_data.get('price')
        
        # Validation for size variants
        if is_size_variant:
            # Size variants must have a parent
            if not parent:
                raise forms.ValidationError("Size variants must have a parent product.")
            
            # Size variants must have a size name
            if not size_name:
                raise forms.ValidationError("Size variants must have a size name.")
            
            # Size variants must have a price
            if not price:
                raise forms.ValidationError("Each size variant must have its own price.")
            
            # Check for existing size variants with same name and parent
            if product_name and parent:
                existing = Product.objects.filter(
                    product_name=product_name,
                    parent=parent
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if existing.exists():
                    raise forms.ValidationError(
                        f"A size variant with name '{product_name}' already exists for this parent product."
                    )
        else:
            # Non-variant products cannot have a parent
            if parent:
                raise forms.ValidationError("Non-variant products cannot have a parent.")
            
            # Standalone products must have a price
            if not price:
                raise forms.ValidationError("Standalone products must have a price.")
            
            # Check for existing products with same name (only for parent products)
            if product_name:
                existing = Product.objects.filter(
                    product_name=product_name,
                    parent=None  # Only check parent products
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if existing.exists():
                    raise forms.ValidationError(
                        f"A product with name '{product_name}' already exists."
                    )
        
        return cleaned_data


class ProductImageForm(forms.ModelForm):
    """Form for adding product images with automatic optimization"""
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'sort_order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewImage(this)'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alt text for accessibility'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = (
            "Upload any image format (JPG, PNG, WebP, etc.). "
            "Images will be automatically optimized for web use with minimum dimensions of 400x400px."
        )
    
    def clean_image(self):
        """Validate uploaded image"""
        from .image_utils import ImageOptimizer
        
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_message = ImageOptimizer.validate_image(image)
            if not is_valid:
                raise forms.ValidationError(error_message)
        return image


class BulkBarcodeForm(forms.Form):
    """Form for bulk barcode operations"""
    barcode_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Enter barcodes in format: Product Name|Barcode Value|Type\nProduct Name|Barcode Value|Type'
        }),
        help_text="Format: Product Name|Barcode Value|Type (one per line)"
    )
    
    def clean_barcode_data(self):
        data = self.cleaned_data['barcode_data']
        lines = [line.strip() for line in data.split('\n') if line.strip()]
        
        if not lines:
            raise forms.ValidationError("Please enter at least one barcode.")
        
        processed_lines = []
        for i, line in enumerate(lines, 1):
            parts = line.split('|')
            if len(parts) != 3:
                raise forms.ValidationError(f"Line {i}: Invalid format. Use: Product Name|Barcode Value|Type")
            
            product_name, barcode_value, barcode_type = [part.strip() for part in parts]
            if not product_name or not barcode_value:
                raise forms.ValidationError(f"Line {i}: Product name and barcode value are required.")
            
            processed_lines.append({
                'product_name': product_name,
                'barcode_value': barcode_value,
                'barcode_type': barcode_type
            })
        
        return processed_lines


class ReviewForm(forms.ModelForm):
    """Form for product reviews"""
    class Meta:
        model = ProductReview
        fields = ['stars', 'content']
        widgets = {
            'stars': forms.Select(attrs={
                'class': 'form-control',
                'choices': [(i, i) for i in range(1, 6)]
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your review here...'
            })
        }