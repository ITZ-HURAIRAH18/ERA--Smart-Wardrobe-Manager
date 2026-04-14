from django.urls import path
from . import views
from . import views_ecommerce

urlpatterns = [
    # ========================================================================
    # MAIN PAGES - New E-commerce system (primary)
    # ========================================================================
    path('', views.home_view, name='home'),
    path('shopping/', views.shop_view, name='shopping'),
    path('product/<slug:slug>/', views.product_detail_new, name='product_detail_new'),

    # ========================================================================
    # CART & CHECKOUT (Django User-based - Primary)
    # ========================================================================
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # ========================================================================
    # AUTH (Django User-based - Primary)
    # ========================================================================
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # ========================================================================
    # STATIC PAGES
    # ========================================================================
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # ========================================================================
    # WISHLIST
    # ========================================================================
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # ========================================================================
    # REVIEWS
    # ========================================================================
    path('review/submit/<int:product_id>/', views.submit_review, name='submit_review'),

    # ========================================================================
    # ADMIN (Django User-based) - Uses new OrderNew model
    # ========================================================================
    path('dashboard/', views_ecommerce.admin_dashboard, name='admin_dashboard'),
    path('dashboard/products/', views_ecommerce.list_products, name='list_products'),
    path('dashboard/products/add/', views_ecommerce.add_product, name='add_product'),
    path('dashboard/products/edit/<int:pk>/', views_ecommerce.edit_product, name='edit_product'),
    path('dashboard/products/delete/<int:pk>/', views_ecommerce.delete_product, name='delete_product'),
    path('dashboard/categories/', views_ecommerce.list_categories, name='list_categories'),
    path('dashboard/categories/add/', views_ecommerce.add_category, name='add_category'),
    path('dashboard/categories/edit/<int:pk>/', views_ecommerce.edit_category, name='edit_category'),
    path('dashboard/categories/delete/<int:pk>/', views_ecommerce.delete_category, name='delete_category'),
    path('dashboard/orders/', views_ecommerce.admin_orders, name='admin_orders'),
    path('dashboard/orders/<int:order_id>/', views_ecommerce.order_detail_admin, name='order_detail_admin'),
    path('dashboard/customers/', views_ecommerce.admin_customers, name='admin_customers'),

    # ========================================================================
    # LEGACY URLS (backward compatibility - Old session-based system)
    # ========================================================================
    path('home1/', views.home1, name='home1'),
    path('landing/', views.landing, name='landing'),
    path('shopping-old/', views.home, name='shopping_old'),
    path('product-old/<int:product_id>/', views.product_detail, name='product_detail_old'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('signout1/', views.signout1, name='signout1'),
    path('cart-old/', views.cart, name='cart_old'),
    path('checkout-old/', views.checkout, name='checkout_old'),
    path('order/', views.order, name='order'),
    path('finalorder/', views.finalorder, name='finalorder'),
    path('order/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('profile-old/', views.profile, name='profile_old'),
    path('rating/submit/', views.submit_rating, name='submit_rating_old'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/', views.remove_cart_item, name='remove_cart_item'),
    path('update-order-status/', views.update_order_status, name='update_order_status'),
    path('newsletter/', views.newsletter_signup, name='newsletter_signup'),
    path('export-orders-csv/', views.export_orders_csv, name='export_orders_csv'),

    # Legacy CRUD
    path('addcat/', views.addcat, name='addcat'),
    path('editcat/<int:id>/', views.editcat, name='editcat'),
    path('deletecat/<int:id>/', views.deletecat, name='deletecat'),
    path('listcat/', views.listcat, name='listcat'),
    path('addpro/', views.addpro, name='addpro'),
    path('listpro/', views.listpro, name='listpro'),
    path('editpro/<int:id>/', views.editpro, name='editpro'),
    path('deletepro/<int:id>/', views.deletepro, name='deletepro'),
    path('add/', views.add, name='add'),
    path('contact-old/', views.contact, name='contact_old'),
    path('about-old/', views.about, name='about_old'),
]
