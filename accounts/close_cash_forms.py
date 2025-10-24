"""
Django forms for Close Cash submission
"""
from django import forms
from django.forms import formset_factory, BaseFormSet


class GeneralSectionForm(forms.Form):
    """General information section"""
    black_market_daily_rate = forms.DecimalField(
        label="Black Market Daily Rate",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    cashier_name = forms.CharField(
        label="Cashier Name",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        label="Date",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    shift_time = forms.ChoiceField(
        label="Shift Time",
        choices=[
            ('', 'Select...'),
            ('Morning', 'Morning'),
            ('Day', 'Day'),
            ('Evening', 'Evening'),
            ('Night', 'Night'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class LebaneseCashForm(forms.Form):
    """Lebanese cash section"""
    lebanese_5000_qty = forms.IntegerField(
        label="5,000",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    lebanese_10000_qty = forms.IntegerField(
        label="10,000",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    lebanese_20000_qty = forms.IntegerField(
        label="20,000",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    lebanese_50000_qty = forms.IntegerField(
        label="50,000",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    lebanese_100000_qty = forms.IntegerField(
        label="100,000",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )


class DollarCashForm(forms.Form):
    """Dollar cash section"""
    dollar_1_qty = forms.IntegerField(
        label="$1",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    dollar_5_qty = forms.IntegerField(
        label="$5",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    dollar_10_qty = forms.IntegerField(
        label="$10",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    dollar_20_qty = forms.IntegerField(
        label="$20",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    dollar_50_qty = forms.IntegerField(
        label="$50",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    dollar_100_qty = forms.IntegerField(
        label="$100",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    dollar_rate = forms.DecimalField(
        label="Dollar Rate",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )


class SpecialCreditForm(forms.Form):
    """Special Credit section"""
    rayan_invoices_credit = forms.DecimalField(
        label="Rayan Invoices Credit",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    employee_invoice_credit = forms.DecimalField(
        label="Employee Invoice Credit",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    delivery_shabeb_co = forms.DecimalField(
        label="Delivery Shabeb Co.",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    delivery_employee = forms.DecimalField(
        label="Delivery Employee",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    waste_goods = forms.DecimalField(
        label="Waste Goods",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )


class CreditEntryForm(forms.Form):
    """Individual credit entry"""
    amount = forms.DecimalField(
        label="Amount",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    currency = forms.ChoiceField(
        label="Currency",
        choices=[
            ('', 'Select...'),
            ('Lebanese', 'Lebanese'),
            ('Dollar', 'Dollar'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        label="Name",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tag = forms.ChoiceField(
        label="Tag",
        choices=[
            ('', 'Select...'),
            ('Cash purchase', 'Cash purchase'),
            ('Credit invoices', 'Credit invoices'),
            ('Employee OTH', 'Employee OTH'),
            ('Customer OTH', 'Customer OTH'),
            ('Bar OTH', 'Bar OTH'),
            ('Store', 'Store'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CoffeeMachineEntryForm(forms.Form):
    """Individual coffee machine entry"""
    current_amount = forms.DecimalField(
        label="Current Amount",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    daily_add = forms.DecimalField(
        label="Daily Add",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
    )
    tag = forms.ChoiceField(
        label="Tag",
        choices=[
            ('', 'Select...'),
            ('Paper Cup Small', 'Paper Cup Small'),
            ('Paper Cup Big', 'Paper Cup Big'),
            ('Plastic Cup Small', 'Plastic Cup Small'),
            ('Cover Cup Big', 'Cover Cup Big'),
            ('Cover Cup Small', 'Cover Cup Small'),
            ('Small Sticks', 'Small Sticks'),
            ('Big Sticks', 'Big Sticks'),
            ('Nescafe Shalimon', 'Nescafe Shalimon'),
            ('Coffee Kg.', 'Coffee Kg.'),
            ('Nescafe Kg.', 'Nescafe Kg.'),
            ('Coffee Mate Kg.', 'Coffee Mate Kg.'),
            ('Cadbury Pouder Kg.', 'Cadbury Pouder Kg.'),
            ('Sugar kg.', 'Sugar kg.'),
            ('Tea Bags.', 'Tea Bags.'),
            ('Nestle kg.', 'Nestle kg.'),
            ('Galon 10L.', 'Galon 10L.'),
            ('Zanjabil w 3asal', 'Zanjabil w 3asal'),
            ('Gaz 12.5 kg.', 'Gaz 12.5 kg.'),
            ('Gaz 10 kg.', 'Gaz 10 kg.'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# Create formsets for dynamic lists
CreditEntryFormSet = formset_factory(
    CreditEntryForm,
    extra=1,
    can_delete=True,
    formset=BaseFormSet
)

CoffeeMachineEntryFormSet = formset_factory(
    CoffeeMachineEntryForm,
    extra=1,
    can_delete=True,
    formset=BaseFormSet
)
