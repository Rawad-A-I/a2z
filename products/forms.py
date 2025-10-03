from django import forms
from .models import Product, Category, Barcode, ColorVariant, SizeVariant
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
    """Form for employees to insert new products"""
    class Meta:
        model = Product
        fields = [
            'product_name', 'category', 'price', 'product_description',
            'product_image', 'is_in_stock', 'stock_quantity', 'dimensions'
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
            'product_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description'
            }),
            'product_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10x5x3 cm'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.fields['is_in_stock'].initial = True
        self.fields['stock_quantity'].initial = 0


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