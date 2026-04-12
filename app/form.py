from django import forms
from django.contrib.auth.models import User
from .models import (
    Cat, Std, Order, Rating,
    Category, Product, OrderNew, Review, Customer
)


# =============================================================================
# EXISTING FORMS (backward compatibility)
# =============================================================================

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


# =============================================================================
# NEW E-COMMERCE FORMS (per prompt.txt specification)
# =============================================================================

class NewProductForm(forms.ModelForm):
    """Form for adding/editing products with image preview."""
    class Meta:
        model = Product
        fields = ['name', 'slug', 'category', 'description', 'price', 'discount_price',
                  'image', 'stock', 'is_featured', 'is_new']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-era',
                'placeholder': 'Enter product name',
                'id': 'product-name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-era',
                'placeholder': 'auto-generated-from-name',
                'readonly': True
            }),
            'category': forms.Select(attrs={'class': 'form-era'}),
            'description': forms.Textarea(attrs={
                'class': 'form-era',
                'rows': 5,
                'placeholder': 'Describe the product...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-era',
                'step': '0.01',
                'min': '0'
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'form-era',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Optional'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-era',
                'min': '0'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NewCategoryForm(forms.ModelForm):
    """Form for adding/editing categories with image preview."""
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-era',
                'placeholder': 'Category name',
                'id': 'category-name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-era',
                'placeholder': 'auto-generated',
                'readonly': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-era',
                'rows': 4,
                'placeholder': 'Describe this category...'
            }),
        }


class CheckoutForm(forms.Form):
    """Checkout form for shipping address."""
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        max_length=200,
        widget=forms.EmailInput(attrs={'class': 'form-era', 'placeholder': 'john@example.com'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': '+1 234 567 8900'})
    )
    address_line1 = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': '123 Fashion Street'})
    )
    address_line2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'Apt 4B (optional)'})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'New York'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'NY'})
    )
    zip_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': '10001'})
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'United States'})
    )


class ProfileForm(forms.ModelForm):
    """Profile update form."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-era', 'placeholder': 'email@example.com'}),
        }


class ReviewForm(forms.ModelForm):
    """Product review form with star rating."""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-era',
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            }),
        }


class ContactForm(forms.Form):
    """Contact form."""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'Your name'})
    )
    email = forms.EmailField(
        max_length=200,
        widget=forms.EmailInput(attrs={'class': 'form-era', 'placeholder': 'your@email.com'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'Subject'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-era',
            'rows': 6,
            'placeholder': 'Your message...'
        })
    )


class CustomerProfileForm(forms.ModelForm):
    """Customer profile form (for session-based auth)."""
    class Meta:
        model = Customer
        fields = ['fname', 'lname', 'phone', 'profile_picture']
        widgets = {
            'fname': forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'First name'}),
            'lname': forms.TextInput(attrs={'class': 'form-era', 'placeholder': 'Last name'}),
            'phone': forms.TextInput(attrs={'class': 'form-era', 'placeholder': '+1 234 567 8900'}),
        }
