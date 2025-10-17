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


class ProductInsertionForm(forms.ModelForm):
    """Form for employees to insert new products with all characteristics"""
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
        self.fields['parent'].queryset = Product.objects.all()
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = "Select parent product (optional)"
        
        self.fields['related_products'].queryset = Product.objects.all()
        self.fields['related_products'].required = False
        
        self.fields['bundle_products'].queryset = Product.objects.all()
        self.fields['bundle_products'].required = False
        
        # Make variant fields optional
        self.fields['color_variant'].required = False
        self.fields['size_variant'].required = False


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