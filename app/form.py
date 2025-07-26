from django import forms

from .models import Cat,Std,Order

class CatForm(forms.ModelForm):
    class Meta:
        model = Cat
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Std
        fields = ['name', 'price', 'category', 'description', 'image']
    
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer', 'quantity', 'price', 'address', 'Phone_no', 'Price', 'date', 'status']