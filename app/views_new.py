"""
ERA E-Commerce Views - Complete Implementation
Includes both legacy (session-based) and new (Django User-based) views
"""
import datetime
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login as django_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import (
    # Legacy models
    Std, Cat, Customer, Order, Cart, CartItem, Rating, Wishlist, Coupon, Newsletter,
    # New models
    Category, Product, OrderNew, OrderItem, CartNew, CartItemNew, Review
)
from .form import (
    CatForm, ProductForm, OrderForm, RatingForm,
    NewProductForm, NewCategoryForm, CheckoutForm, ProfileForm, ReviewForm, ContactForm, CustomerProfileForm
)


# =============================================================================
# HELPER DECORATORS
# =============================================================================

def login_required_custom(view_func):
    """Decorator to check if customer is logged in via session OR Django auth."""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        if request.session.get('customer_id'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Please login to access this page.')
        return redirect('login')
    return _wrapped_view


def staff_member_required(view_func):
    """Decorator to check if logged-in user is staff (admin)."""
    def _wrapped_view(request, *args, **kwargs):
        is_admin = False
        if request.user.is_authenticated and request.user.is_staff:
            is_admin = True
        elif request.session.get('customer_id'):
            try:
                customer = Customer.objects.get(id=request.session.get('customer_id'))
                if customer.email == 'admin@era.com':
                    is_admin = True
            except Customer.DoesNotExist:
                pass

        if not is_admin:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

def login_view(request):
    """Unified login for both admins and regular users."""
    if request.method == 'GET':
        return render(request, 'login.html')
    
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    if not email or not password:
        return render(request, 'login.html', {
            'error': 'Please enter both email and password.',
            'values': {'email': email}
        })

    # Try Django User authentication first (admin/staff)
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            django_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
    except User.DoesNotExist:
        pass

    # Try Customer (session-based)
    try:
        customer_instance = Customer.get_customer_by_email(email)
        if customer_instance and customer_instance.password == password:
            request.session['customer_id'] = customer_instance.id
            request.session['customer_email'] = customer_instance.email
            request.session['customer_name'] = customer_instance.fname
            messages.success(request, f'Welcome back, {customer_instance.fname}!')
            if customer_instance.email == 'admin@era.com':
                return redirect('admin_dashboard')
            return redirect('home')
    except Exception:
        pass

    return render(request, 'login.html', {
        'error': 'Invalid email or password. Please try again.',
        'values': {'email': email}
    })


def register_view(request):
    """User registration for Django User model."""
    if request.method == 'GET':
        return render(request, 'register.html')
    
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    # Validation
    if not all([first_name, last_name, username, email, password, confirm_password]):
        messages.error(request, 'All fields are required.')
        return render(request, 'register.html', {'values': request.POST})

    if password != confirm_password:
        messages.error(request, 'Passwords do not match.')
        return render(request, 'register.html', {'values': request.POST})

    if len(password) < 6:
        messages.error(request, 'Password must be at least 6 characters.')
        return render(request, 'register.html', {'values': request.POST})

    if User.objects.filter(email=email).exists():
        messages.error(request, 'Email already registered.')
        return render(request, 'register.html', {'values': request.POST})

    if User.objects.filter(username=username).exists():
        messages.error(request, 'Username already taken.')
        return render(request, 'register.html', {'values': request.POST})

    # Create user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error creating account: {str(e)}')
        return render(request, 'register.html', {'values': request.POST})


def logout_view(request):
    """Logout and clear session."""
    if request.user.is_authenticated:
        django_logout(request)
    request.session.clear()
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def signup(request):
    """Custom Customer registration (legacy)."""
    if request.method == 'GET':
        return render(request, 'signup.html', {'values': {}})
    
    postData = request.POST
    f_name = postData.get('firstname')
    l_name = postData.get('lastname')
    phoneno = postData.get('phone')
    Email = postData.get('email')
    Password = postData.get('password')

    if not all([f_name, l_name, phoneno, Email, Password]):
        return render(request, 'signup.html', {
            'error': 'All fields are required!',
            'values': postData
        })

    customer_instance = Customer(fname=f_name, lname=l_name, phone=phoneno, email=Email, password=Password)

    if customer_instance.is_exit():
        return render(request, 'signup.html', {
            'error': 'Email already exists!',
            'values': postData
        })

    customer_instance.reg()
    messages.success(request, 'Account created successfully! Please login.')
    return redirect('login')


def signout(request):
    """Logout and redirect to login."""
    request.session.clear()
    return redirect('login')


def signout1(request):
    """Logout and redirect to home."""
    request.session.clear()
    return redirect('home')


# =============================================================================
# HOME / SHOPPING VIEWS
# =============================================================================

def home(request):
    """Shopping page with category filtering, cart updates, and search/filter."""
    if request.method == 'GET':
        categories = Cat.get_all_pro()
        cat_id = request.GET.get('category')
        search_query = request.GET.get('q', '').strip()
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        sort_by = request.GET.get('sort', '-created_at')

        products = Std.objects.filter(is_active=True)

        if cat_id:
            products = products.filter(category_id=cat_id)

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        if min_price:
            try:
                products = products.filter(price__gte=int(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                products = products.filter(price__lte=int(max_price))
            except ValueError:
                pass

        valid_sort_fields = ['price', '-price', 'name', '-name', 'created_at', '-created_at']
        if sort_by in valid_sort_fields:
            products = products.order_by(sort_by)
        else:
            products = products.order_by('-created_at')

        products = products.annotate(annotated_avg_rating=Avg('ratings__stars')).distinct()

        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        products_page = paginator.get_page(page_number)

        return render(request, 'home.html', {
            'products': products_page,
            'categories': categories,
            'current_category': cat_id,
            'search_query': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by,
        })

    elif request.method == 'POST':
        product_id = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})
        
        if cart:
            quantity = cart.get(product_id)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product_id)
                    else:
                        cart[product_id] = quantity - 1
                else:
                    cart[product_id] = quantity + 1
            else:
                cart[product_id] = 1
        else:
            cart = {product_id: 1}

        request.session['cart'] = cart

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'cart': cart,
                'cart_count': sum(cart.values())
            })

        return redirect('home')


def shop_view(request):
    """Shop page using new Product model."""
    categories = Category.objects.all().order_by('name')
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', '-created_at')
    is_featured = request.GET.get('featured')

    products = Product.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if is_featured:
        products = products.filter(is_featured=True)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    valid_sort = ['price', '-price', 'name', '-name', 'created_at', '-created_at']
    if sort_by in valid_sort:
        products = products.order_by(sort_by)

    products = products.annotate(avg_review_rating=Avg('reviews__rating'))

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    return render(request, 'shopping.html', {
        'products': products_page,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })


def landing(request):
    """Premium landing page."""
    featured_products = Product.objects.filter(is_featured=True)[:8]
    new_products = Product.objects.filter(is_new=True)[:8]
    return render(request, 'landing.html', {
        'featured_products': featured_products,
        'new_products': new_products,
    })


def home1(request):
    """Original landing page."""
    return render(request, 'home1.html')


def about_view(request):
    """About page."""
    return render(request, 'about.html')


def contact_view(request):
    """Contact page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, f'Thank you {form.cleaned_data["name"]}! Your message has been received.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})


def add(request):
    """Generic add page."""
    return render(request, 'add.html')


# =============================================================================
# PRODUCT DETAIL VIEW
# =============================================================================

def product_detail(request, product_id):
    """Product detail page (legacy Std model)."""
    product = get_object_or_404(Std, id=product_id, is_active=True)
    ratings = product.ratings.all().order_by('-created_at')
    avg_rating = ratings.aggregate(Avg('stars'))['stars__avg'] or 0
    rating_count = ratings.count()

    customer_id = request.session.get('customer_id')
    user_has_rated = False
    user_review = None
    if customer_id:
        try:
            user_review = Rating.objects.get(product=product, customer_id=customer_id)
            user_has_rated = True
        except Rating.DoesNotExist:
            pass

    related_products = Std.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]

    in_wishlist = False
    if customer_id:
        in_wishlist = Wishlist.objects.filter(customer_id=customer_id, product=product).exists()

    cart = request.session.get('cart', {})
    cart_quantity = cart.get(str(product_id), 0)

    return render(request, 'product_detail.html', {
        'product': product,
        'ratings': ratings[:10],
        'avg_rating': round(avg_rating, 1),
        'rating_count': rating_count,
        'user_has_rated': user_has_rated,
        'user_review': user_review,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'cart_quantity': cart_quantity,
        'available_sizes': product.available_sizes.split(',') if product.available_sizes else [],
        'available_colors': product.available_colors.split(',') if product.available_colors else [],
    })


def product_detail_new(request, slug):
    """Product detail page using new Product model."""
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all().order_by('-created_at')[:10]
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()

    user_has_reviewd = False
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(product=product, user=request.user)
            user_has_reviewd = True
        except Review.DoesNotExist:
            pass

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    in_wishlist = False
    cart_quantity = 0
    if request.user.is_authenticated:
        try:
            cart = CartNew.objects.get(user=request.user)
            cart_item = cart.items.filter(product=product).first()
            if cart_item:
                cart_quantity = cart_item.quantity
        except CartNew.DoesNotExist:
            pass

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'user_has_reviewd': user_has_reviewd,
        'user_review': user_review,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'cart_quantity': cart_quantity,
    })


# =============================================================================
# CART VIEWS (New System - Django User-based)
# =============================================================================

@login_required
def cart_view(request):
    """Display cart with product details and calculated totals."""
    cart, _ = CartNew.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    
    subtotal = sum(item.get_total() for item in items)
    shipping = 0 if subtotal >= 200 else 15
    total = subtotal + shipping
    free_delivery_remaining = max(0, 200 - float(subtotal))

    return render(request, 'cart.html', {
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'free_delivery_remaining': free_delivery_remaining
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart."""
    product = get_object_or_404(Product, id=product_id)
    cart, _ = CartNew.objects.get_or_create(user=request.user)
    
    selected_size = request.POST.get('size', '')
    selected_color = request.POST.get('color', '')
    
    item, created = CartItemNew.objects.get_or_create(
        cart=cart, 
        product=product,
        selected_size=selected_size,
        selected_color=selected_color
    )
    
    if not created:
        item.quantity += 1
        item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'shopping'))


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    item = get_object_or_404(CartItemNew, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
@require_POST
def update_cart(request, item_id):
    """Update cart item quantity."""
    item = get_object_or_404(CartItemNew, id=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    
    if qty > 0:
        item.quantity = qty
        item.save()
    else:
        item.delete()
        messages.success(request, 'Item removed from cart.')
    
    return redirect('cart')


@login_required
def clear_cart(request):
    """Clear all items from cart."""
    try:
        cart = CartNew.objects.get(user=request.user)
        cart.items.all().delete()
        messages.success(request, 'Cart cleared.')
    except CartNew.DoesNotExist:
        pass
    return redirect('cart')


# =============================================================================
# CHECKOUT VIEWS
# =============================================================================

@login_required
def checkout_view(request):
    """Checkout with shipping address and order creation."""
    cart = get_object_or_404(CartNew, user=request.user)
    items = cart.items.select_related('product').all()
    
    if not items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    subtotal = sum(item.get_total() for item in items)
    shipping = 0 if subtotal >= 200 else 15
    total = subtotal + shipping

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = f"{form.cleaned_data['address_line1']}"
            if form.cleaned_data['address_line2']:
                address += f", {form.cleaned_data['address_line2']}"
            address += f"\n{form.cleaned_data['city']}, {form.cleaned_data['state']} {form.cleaned_data['zip_code']}"
            address += f"\n{form.cleaned_data['country']}"

            estimated_delivery = timezone.now().date() + datetime.timedelta(days=7)
            tracking_number = f"ERA{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

            order = OrderNew.objects.create(
                user=request.user,
                total_amount=total,
                shipping_address=address,
                tracking_number=tracking_number,
                estimated_delivery=estimated_delivery
            )

            for item in items:
                product = item.product
                product_image = product.image  # Snapshot the product image
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    image=product_image,
                    quantity=item.quantity,
                    price=product.discount_price or product.price
                )
                # Reduce stock
                product.stock -= item.quantity
                product.save()

            cart.items.all().delete()
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
        })

    return render(request, 'checkout.html', {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    })


def order_confirmation(request, order_id):
    """Order confirmation page."""
    order = get_object_or_404(OrderNew, id=order_id, user=request.user)
    items = order.items.select_related('product').all()
    
    return render(request, 'order_confirmation.html', {
        'order': order,
        'items': items
    })


# =============================================================================
# USER VIEWS
# =============================================================================

@login_required
def my_orders(request):
    """User's order history."""
    orders = OrderNew.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """User's order detail."""
    order = get_object_or_404(OrderNew, id=order_id, user=request.user)
    items = order.items.select_related('product').all()
    return render(request, 'order_detail.html', {
        'order': order,
        'items': items
    })


@login_required
def profile_view(request):
    """User profile page."""
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        elif 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully!')
                return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    orders = OrderNew.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    order_stats = OrderNew.objects.filter(user=request.user).aggregate(
        total_orders=Count('id'),
        total_spent=Sum('total_amount'),
    )

    return render(request, 'profile.html', {
        'form': form,
        'orders': orders,
        'order_stats': order_stats
    })


# =============================================================================
# WISHLIST VIEWS
# =============================================================================

@login_required_custom
def view_wishlist(request):
    """View wishlist items."""
    customer_id = request.session.get('customer_id')
    wishlist_items = Wishlist.objects.filter(customer_id=customer_id).select_related('product')
    
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0

    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items,
        'cart_count': cart_count,
    })


@login_required_custom
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    customer_id = request.session.get('customer_id')
    product = get_object_or_404(Std, id=product_id, is_active=True)

    try:
        Wishlist.objects.get_or_create(customer_id=customer_id, product=product)
        messages.success(request, f'{product.name} added to wishlist!')
    except IntegrityError:
        messages.info(request, f'{product.name} is already in your wishlist.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Added to wishlist'})

    return redirect('product_detail', product_id=product_id)


@login_required_custom
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    customer_id = request.session.get('customer_id')
    try:
        wishlist_item = Wishlist.objects.get(customer_id=customer_id, product_id=product_id)
        wishlist_item.delete()
        messages.success(request, 'Item removed from wishlist.')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Item not found in wishlist.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Removed from wishlist'})

    return redirect('wishlist')


@login_required_custom
def toggle_wishlist(request, product_id):
    """Toggle wishlist via AJAX."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        customer_id = request.session.get('customer_id')
        product = get_object_or_404(Std, id=product_id, is_active=True)

        try:
            wishlist_item = Wishlist.objects.get(customer_id=customer_id, product=product)
            wishlist_item.delete()
            in_wishlist = False
            message = f'{product.name} removed from wishlist.'
        except Wishlist.DoesNotExist:
            Wishlist.objects.create(customer_id=customer_id, product=product)
            in_wishlist = True
            message = f'{product.name} added to wishlist!'

        return JsonResponse({
            'status': 'success',
            'in_wishlist': in_wishlist,
            'message': message
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


# =============================================================================
# REVIEW VIEWS
# =============================================================================

@login_required
@require_POST
def submit_review(request, product_id):
    """Submit product review."""
    product = get_object_or_404(Product, id=product_id)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': form.cleaned_data['rating'],
                'comment': form.cleaned_data['comment']
            }
        )
        if created:
            messages.success(request, 'Review submitted successfully!')
        else:
            messages.success(request, 'Review updated successfully!')
    
    return redirect('product_detail_new', slug=product.slug)


@login_required_custom
def submit_rating(request, product_id):
    """Submit rating (legacy system)."""
    if request.method == 'POST':
        stars = request.POST.get('stars')
        review = request.POST.get('review', '').strip()
        customer_id = request.session.get('customer_id')

        if not stars:
            messages.error(request, 'Please select a rating.')
            return redirect('product_detail', product_id=product_id)

        try:
            stars = int(stars)
            if stars < 1 or stars > 5:
                messages.error(request, 'Rating must be between 1 and 5.')
                return redirect('product_detail', product_id=product_id)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating value.')
            return redirect('product_detail', product_id=product_id)

        rating, created = Rating.objects.update_or_create(
            product_id=product_id,
            customer_id=customer_id,
            defaults={'stars': stars, 'review': review}
        )

        if created:
            messages.success(request, 'Thank you for your review!')
        else:
            messages.success(request, 'Your review has been updated!')

        return redirect('product_detail', product_id=product_id)

    return redirect('home')


# =============================================================================
# ADMIN VIEWS
# =============================================================================

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive stats."""
    thirty_days_ago = timezone.now().date() - datetime.timedelta(days=30)

    # Stats
    total_orders = OrderNew.objects.count()
    total_revenue = OrderNew.objects.filter(status__in=['delivered', 'shipped']).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Count products from BOTH models (new Product + legacy Std)
    new_products_count = Product.objects.count()
    legacy_products_count = Std.objects.count()
    total_products = new_products_count + legacy_products_count
    
    total_customers = User.objects.filter(is_staff=False).count()
    pending_orders = OrderNew.objects.filter(status='pending').count()
    
    # Low stock from both models
    low_stock_new = Product.objects.filter(stock__lt=5, stock__gt=0).count()
    low_stock_legacy = Std.objects.filter(stock_quantity__lt=5, stock_quantity__gt=0, is_active=True).count()
    low_stock = low_stock_new + low_stock_legacy

    # Revenue trend (last 6 months)
    revenue_by_month = []
    for i in range(5, -1, -1):
        month_date = timezone.now() - datetime.timedelta(days=30*i)
        month_revenue = OrderNew.objects.filter(
            created_at__month=month_date.month,
            created_at__year=month_date.year,
            status__in=['delivered', 'shipped']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_by_month.append({
            'month': month_date.strftime('%b'),
            'revenue': float(month_revenue)
        })

    # Orders by status
    orders_by_status = OrderNew.objects.values('status').annotate(count=Count('id'))

    # Top products
    top_products = OrderItem.objects.values(
        'product__id', 'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:5]

    # Recent orders
    recent_orders = OrderNew.objects.select_related('user').order_by('-created_at')[:10]

    return render(request, 'admin/dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'new_products_count': new_products_count,
        'legacy_products_count': legacy_products_count,
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'low_stock': low_stock,
        'revenue_by_month': revenue_by_month,
        'orders_by_status': list(orders_by_status),
        'top_products': list(top_products),
        'recent_orders': recent_orders,
    })


# Admin Product CRUD
@staff_member_required
def add_product(request):
    """Add new product."""
    if request.method == 'POST':
        form = NewProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('list_products')
    else:
        form = NewProductForm()
    
    return render(request, 'admin/add_product.html', {'form': form})


@staff_member_required
def edit_product(request, pk):
    """Edit product."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = NewProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('list_products')
    else:
        form = NewProductForm(instance=product)
    
    return render(request, 'admin/edit_product.html', {'form': form, 'product': product})


@staff_member_required
@require_POST
def delete_product(request, pk):
    """Delete product."""
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('list_products')


@staff_member_required
def list_products(request):
    """List all products with search and filter."""
    products = Product.objects.select_related('category').all()
    
    search = request.GET.get('q', '').strip()
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)
    
    sort = request.GET.get('sort', '-created_at')
    valid_sort = ['price', '-price', 'name', '-name', 'created_at', '-created_at', 'stock', '-stock']
    if sort in valid_sort:
        products = products.order_by(sort)

    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    categories = Category.objects.all()

    return render(request, 'admin/list_products.html', {
        'products': products_page,
        'categories': categories,
        'search': search,
        'sort': sort,
    })


# Admin Category CRUD
@staff_member_required
def add_category(request):
    """Add new category."""
    if request.method == 'POST':
        form = NewCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('list_categories')
    else:
        form = NewCategoryForm()
    
    return render(request, 'admin/add_category.html', {'form': form})


@staff_member_required
def edit_category(request, pk):
    """Edit category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = NewCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('list_categories')
    else:
        form = NewCategoryForm(instance=category)
    
    return render(request, 'admin/edit_category.html', {'form': form, 'category': category})


@