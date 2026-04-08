from django.contrib import admin
from .models import Std, Cat, Customer, Order, Cart, CartItem, Rating, Wishlist, Coupon, Newsletter


class AdminProduct(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'description', 'stock_quantity', 'is_active', 'created_at']
    list_editable = ['stock_quantity', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']


class AdminCat(admin.ModelAdmin):
    list_display = ['name']


class AdminOrder(admin.ModelAdmin):
    list_display = ['id', 'customer', 'product', 'quantity', 'price', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['customer__fname', 'customer__lname']


class AdminRating(admin.ModelAdmin):
    list_display = ['product', 'customer', 'stars', 'created_at']
    list_filter = ['stars']


class AdminCoupon(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'active', 'expiry_date', 'min_order_value']
    list_filter = ['active']


admin.site.register(Std, AdminProduct)
admin.site.register(Cat, AdminCat)
admin.site.register(Customer)
admin.site.register(Order, AdminOrder)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Rating, AdminRating)
admin.site.register(Wishlist)
admin.site.register(Coupon, AdminCoupon)
admin.site.register(Newsletter)
