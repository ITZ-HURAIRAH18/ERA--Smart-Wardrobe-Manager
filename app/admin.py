from django.contrib import admin
from .models import (
    Std, Cat, Customer, Order, Cart, CartItem, Rating, Wishlist, Coupon, Newsletter,
    Category, Product, OrderNew, OrderItem, CartNew, CartItemNew, Review
)


# =============================================================================
# EXISTING ADMIN CONFIGURATION
# =============================================================================

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


# =============================================================================
# NEW E-COMMERCE ADMIN CONFIGURATION
# =============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at', 'product_count']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'discount_price',
        'stock', 'is_featured', 'is_new', 'created_at'
    ]
    list_filter = ['category', 'is_featured', 'is_new']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_featured']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price'),
            'classes': ('collapse',)
        }),
        ('Inventory', {
            'fields': ('stock',),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_new', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderNew)
class OrderNewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'status', 'total_amount',
        'created_at', 'get_items_count'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_editable = ['status']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'tracking_number')
        }),
        ('Financial', {
            'fields': ('total_amount',)
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'estimated_delivery')
        }),
        ('Additional', {
            'fields': ('note', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_items_count(self, obj):
        return obj.get_items_count()
    get_items_count.short_description = 'Items'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total']

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total']
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__id']

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'


@admin.register(CartNew)
class CartNewAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'get_subtotal', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    def items_count(self, obj):
        return obj.items_count()
    items_count.short_description = 'Items'

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


@admin.register(CartItemNew)
class CartItemNewAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_total']
    list_filter = ['cart__user']
    search_fields = ['product__name', 'cart__user__email']

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


# Admin site customization
admin.site.site_header = 'ERA Fashion Administration'
admin.site.site_title = 'ERA Admin'
admin.site.index_title = 'Welcome to ERA Admin Panel'
