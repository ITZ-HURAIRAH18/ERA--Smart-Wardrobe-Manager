from django import forms
from .models import Cat, Std, Order, Rating


class CatForm(forms.ModelForm):
    class Meta:
        model = Cat
        fields = ['name']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Std
        fields = ['name', 'price', 'category', 'description', 'image', 'available_sizes', 'available_colors', 'stock_quantity', 'is_active']
        widgets = {
            'available_sizes': forms.TextInput(attrs={'placeholder': 'S,M,L,XL', 'help_text': 'Comma-separated sizes'}),
            'available_colors': forms.TextInput(attrs={'placeholder': 'Red,Blue,Black', 'help_text': 'Comma-separated colors'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer', 'quantity', 'price', 'address', 'Phone_no', 'date', 'status', 'tracking_number', 'estimated_delivery']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'review']
        widgets = {
            'stars': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review...'}),
        }
