from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Cat, Std, Order, Rating


class CatForm(forms.ModelForm):
    class Meta:
        model = Cat
        fields = ['name']


class ProductForm(forms.ModelForm):
    image_url = forms.URLField(
        required=False,
        label="Or paste image URL",
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com/image.jpg',
            'class': 'form-control',
        }),
        help_text="Enter a direct link to an image (e.g. https://example.com/product.jpg)",
    )

    class Meta:
        model = Std
        fields = ['name', 'price', 'category', 'description', 'image', 'image_url',
                  'available_sizes', 'available_colors', 'stock_quantity', 'is_active']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'available_sizes': forms.TextInput(attrs={
                'placeholder': 'S,M,L,XL',
                'help_text': 'Comma-separated sizes',
                'class': 'form-control',
            }),
            'available_colors': forms.TextInput(attrs={
                'placeholder': 'Red,Blue,Black',
                'help_text': 'Comma-separated colors',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'image': 'Upload Image',
        }

    def clean(self):
        """Ensure at least one of image or image_url is provided."""
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        image_url = cleaned_data.get('image_url')

        # Check if we're editing an existing product (instance has an image already)
        is_editing = self.instance and self.instance.pk

        if not image and not image_url:
            if not is_editing or (is_editing and not self.instance.image and not self.instance.image_url):
                raise ValidationError(
                    "Please provide either an uploaded image or an image URL."
                )

        # Validate URL format if provided
        if image_url:
            url_validator = URLValidator()
            try:
                url_validator(image_url)
            except ValidationError:
                raise ValidationError({
                    'image_url': "Please enter a valid URL (e.g. https://example.com/image.jpg)"
                })

        return cleaned_data


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
