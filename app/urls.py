from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('shopping', views.home, name='home'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('add', views.add, name='add'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Auth
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('signout/', views.signout, name='signout'),
    path('signout1/', views.signout1, name='signout1'),

    # Cart & Checkout
    path('cart/', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('finalorder', views.finalorder, name='finalorder'),
    path('order/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),

    # Customer orders
    path('order', views.order, name='order'),

    # Profile
    path('profile/', views.profile, name='profile'),

    # Wishlist
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Rating
    path('rating/submit/', views.submit_rating, name='submit_rating'),

    # AJAX endpoints
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/', views.remove_cart_item, name='remove_cart_item'),
    path('update-order-status/', views.update_order_status, name='update_order_status'),

    # Category CRUD
    path('addcat', views.addcat, name='addcat'),
    path('edit/<int:id>/', views.editcat, name='editcat'),
    path('del/<int:id>/', views.deletecat, name='deletecat'),
    path('listcat', views.listcat, name='listcat'),

    # Product CRUD
    path('addpro', views.addpro, name='addpro'),
    path('listpro', views.listpro, name='listpro'),
    path('editpro/<int:id>/', views.editpro, name='editpro'),
    path('deletepro/<int:id>/', views.deletepro, name='deletepro'),

    # Newsletter
    path('newsletter/', views.newsletter_signup, name='newsletter_signup'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('export-orders-csv/', views.export_orders_csv, name='export_orders_csv'),

    # Landing page (must be last to avoid conflicts)
    path('', views.home1, name='home1'),
]
