from django.contrib import admin
from .models import Std, Cat,Customer,Order

class AdminProduct(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'description']

class AdminCat(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Std, AdminProduct)
admin.site.register(Cat, AdminCat)
admin.site.register(Customer)
admin.site.register(Order)
