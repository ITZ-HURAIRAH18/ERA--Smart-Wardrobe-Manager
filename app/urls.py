from django.urls import path
from . import views

urlpatterns = [
    path('shopping', views.home, name='home'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('add', views.add, name='add'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('signout/', views.signout, name='signout'),
    path('cart/', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('order', views.order, name='order'),
    path('addcat', views.addcat, name='addcat'),
    path('edit/<int:id>/', views.editcat, name='editcat'),  # Correct name 'editcat'
    path('del/<int:id>/', views.deletecat, name='deletecat'),
    path('listcat', views.listcat, name='listcat'),
    path('addpro', views.addpro, name='addpro'),
    path('listpro', views.listpro, name='listpro'),  # List products
    path('editpro/<int:id>/', views.editpro, name='editpro'),  # Edit product
    path('deletepro/<int:id>/', views.deletepro, name='deletepro'),  # Delete product
    path('', views.home1, name='home1'),
    path('finalorder', views.finalorder, name='finalorder'),
       path('order/<int:order_id>/edit/', views.edit_order, name='edit_order'),
]
