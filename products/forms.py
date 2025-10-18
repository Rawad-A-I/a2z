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
        # Show all products as potential parents, but prefer standalone products
        self.fields['parent'].queryset = Product.objects.filter(parent=None).order_by('product_name')
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
        category = cleaned_data.get('category')
        
        # Store validation errors
        errors = []
        warnings = []
        
        # Basic validation
        if not product_name or len(product_name.strip()) < 2:
            errors.append("Product name must be at least 2 characters long.")
        
        if not category:
            errors.append("Please select a category for the product.")
        
        # Validation for size variants
        if is_size_variant:
            # Size variants must have a parent
            if not parent:
                errors.append("⚠️ Size variants must have a parent product selected.")
            
            # Size variants must have a size name
            if not size_name or len(size_name.strip()) < 1:
                errors.append("⚠️ Size variants must have a size name (e.g., Small, Medium, Large).")
            
            # Size variants must have a price
            if not price or price <= 0:
                errors.append("⚠️ Each size variant must have its own price greater than $0.")
            
            # Check for existing size variants with same name and parent
            if product_name and parent and size_name:
                # Check for exact match
                existing = Product.objects.filter(
                    parent=parent,
                    size_name__iexact=size_name.strip()
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if existing.exists():
                    errors.append(f"❌ A size variant '{size_name}' already exists for '{parent.product_name}'. Please choose a different size name.")
                
                # Check for similar size names (warning)
                similar_sizes = Product.objects.filter(
                    parent=parent,
                    size_name__icontains=size_name.strip()
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if similar_sizes.exists():
                    warnings.append(f"⚠️ Similar size names exist for this parent: {', '.join([s.size_name for s in similar_sizes])}")
            
            # Validate size name format
            if size_name and not size_name.strip().replace(' ', '').replace('-', '').isalnum():
                warnings.append("⚠️ Size name should contain only letters, numbers, spaces, and hyphens.")
                
        else:
            # Non-variant products cannot have a parent
            if parent:
                errors.append("❌ Standalone products cannot have a parent. Please uncheck 'Size Variant' or select 'Standalone Product'.")
            
            # Standalone products must have a price
            if not price or price <= 0:
                errors.append("⚠️ Standalone products must have a price greater than $0.")
            
            # Check for existing products with same name (only for parent products)
            if product_name:
                existing = Product.objects.filter(
                    product_name__iexact=product_name.strip(),
                    parent=None  # Only check parent products
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if existing.exists():
                    errors.append(f"❌ A product with name '{product_name}' already exists. Please choose a different name.")
                
                # Check for similar product names (warning)
                similar_products = Product.objects.filter(
                    product_name__icontains=product_name.strip(),
                    parent=None
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if similar_products.exists():
                    warnings.append(f"⚠️ Similar product names exist: {', '.join([p.product_name for p in similar_products[:3]])}")
        
        # Price validation
        if price and price > 0:
            if price > 10000:
                warnings.append("⚠️ Price seems unusually high. Please verify the amount.")
            elif price < 0.01:
                warnings.append("⚠️ Price seems unusually low. Please verify the amount.")
        
        # Category validation
        if category:
            # Check if category has other products (for context)
            category_products = Product.objects.filter(category=category, parent=None).count()
            if category_products > 0:
                warnings.append(f"ℹ️ This category already has {category_products} product(s).")
        
        # Store warnings in cleaned_data for template access
        if warnings:
            cleaned_data['_warnings'] = warnings
        
        # Raise validation errors if any
        if errors:
            raise forms.ValidationError(errors)
        
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