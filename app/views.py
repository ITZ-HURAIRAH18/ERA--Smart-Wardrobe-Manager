from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login as django_login
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.conf import settings
import csv
import datetime
import os

from .models import Std, Cat, Customer, Order, Cart, CartItem, Rating, Wishlist, Coupon, Newsletter
from middleware.auth import auth_middleware


# =============================================================================
# HELPER: Session-based login required decorator
# =============================================================================
def login_required_custom(view_func):
    """Decorator to check if customer is logged in via session."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('customer_id'):
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
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
# HOME / SHOPPING PAGE (with search & filter)
# =============================================================================
def home(request):
    """Shopping page with category filtering (GET), cart updates (POST), and search/filter."""
    if request.method == 'GET':
        categories = Cat.get_all_pro()
        cat_id = request.GET.get('category')
        search_query = request.GET.get('q', '').strip()
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        sort_by = request.GET.get('sort', '-created_at')

        # Base queryset
        products = Std.objects.filter(is_active=True)

        # Category filter
        if cat_id:
            products = products.filter(category_id=cat_id)

        # Search filter using Q objects
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # Price range filter
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

        # Sorting
        valid_sort_fields = ['price', '-price', 'name', '-name', 'created_at', '-created_at']
        if sort_by in valid_sort_fields:
            products = products.order_by(sort_by)
        else:
            products = products.order_by('-created_at')

        # Annotate with average rating (use different name to avoid conflict with model property)
        products = products.annotate(annotated_avg_rating=Avg('ratings__stars')).distinct()

        # Pagination
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        products_page = paginator.get_page(page_number)

        data = {
            'products': products_page,
            'categories': categories,
            'current_category': cat_id,
            'search_query': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by,
        }

        return render(request, 'home.html', data)

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
            cart = {}
            cart[product_id] = 1

        request.session['cart'] = cart

        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'cart': cart,
                'cart_count': sum(cart.values())
            })

        return redirect('home')


# =============================================================================
# LANDING PAGE & STATIC PAGES
# =============================================================================
def home1(request):
    """Landing page."""
    return render(request, 'home1.html')


def about(request):
    """About page."""
    return render(request, 'about.html')


def contact(request):
    """Contact page."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            messages.success(request, f'Thank you {name}! Your message has been received. We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all required fields.')

    return render(request, 'contact.html')


def add(request):
    """Generic add page."""
    return render(request, 'add.html')


# =============================================================================
# PRODUCT DETAIL PAGE
# =============================================================================
def product_detail(request, product_id):
    """Full product detail page with ratings, reviews, and related products."""
    product = get_object_or_404(Std, id=product_id, is_active=True)

    # Get all ratings for this product
    ratings = product.ratings.all().order_by('-created_at')
    avg_rating = ratings.aggregate(Avg('stars'))['stars__avg'] or 0
    rating_count = ratings.count()

    # Check if current user has already rated
    customer_id = request.session.get('customer_id')
    user_has_rated = False
    user_review = None
    if customer_id:
        try:
            user_review = Rating.objects.get(product=product, customer_id=customer_id)
            user_has_rated = True
        except Rating.DoesNotExist:
            pass

    # Related products (same category, excluding current product)
    related_products = Std.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    # Check if in wishlist
    in_wishlist = False
    if customer_id:
        in_wishlist = Wishlist.objects.filter(
            customer_id=customer_id,
            product=product
        ).exists()

    # Check cart quantity
    cart = request.session.get('cart', {})
    cart_quantity = cart.get(str(product_id), 0)

    context = {
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
    }

    return render(request, 'product_detail.html', context)


# =============================================================================
# SUBMIT RATING
# =============================================================================
@login_required_custom
def submit_rating(request, product_id):
    """POST view for rating submission."""
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

        # Update or create rating
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
# AUTHENTICATION: SIGNUP
# =============================================================================
def signup(request):
    """Custom Customer registration."""
    if request.method == 'GET':
        return render(request, 'signup.html', {'values': {}})
    else:
        postData = request.POST
        f_name = postData.get('firstname')
        l_name = postData.get('lastname')
        phoneno = postData.get('phone')
        Email = postData.get('email')
        Password = postData.get('password')

        if not f_name or not l_name or not phoneno or not Email or not Password:
            return render(request, 'signup.html', {
                'error': 'All fields are required!',
                'values': postData
            })

        customer_instance = Customer(
            fname=f_name,
            lname=l_name,
            phone=phoneno,
            email=Email,
            password=Password
        )

        if customer_instance.is_exit():
            return render(request, 'signup.html', {
                'error': 'Email already exists!',
                'values': postData
            })

        customer_instance.reg()
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')


# =============================================================================
# AUTHENTICATION: UNIFIED LOGIN (Bug 13)
# =============================================================================
def login(request):
    """Unified login for both admins and regular users with role-based redirects."""
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        print(f"DEBUG LOGIN: Attempting login for email: {email}")  # Debug log

        if not email or not password:
            print(f"DEBUG LOGIN: Missing email or password")  # Debug log
            return render(request, 'login.html', {
                'error': 'Please enter both email and password.',
                'values': {'email': email}
            })

        try:
            customer_instance = Customer.get_customer_by_email(email)
            print(f"DEBUG LOGIN: Customer found: {customer_instance}")  # Debug log
            
            if customer_instance:
                print(f"DEBUG LOGIN: Stored password: {customer_instance.password}, Input password: {password}")  # Debug log
                print(f"DEBUG LOGIN: Password match: {customer_instance.password == password}")  # Debug log
        except Exception as e:
            print(f"DEBUG LOGIN: Exception occurred: {e}")  # Debug log
            import traceback
            traceback.print_exc()
            return render(request, 'login.html', {
                'error': f'An error occurred during login: {str(e)}',
                'values': {'email': email}
            })

        if customer_instance and customer_instance.password == password:
            # Set session variables
            request.session['customer_id'] = customer_instance.id
            request.session['customer_email'] = customer_instance.email
            request.session['customer_name'] = customer_instance.fname
            messages.success(request, f'Welcome back, {customer_instance.fname}!')

            print(f"DEBUG LOGIN: Login successful for {email}")  # Debug log

            # Role-based redirect
            if customer_instance.email == 'admin@era.com':
                print(f"DEBUG LOGIN: Redirecting to admin dashboard")  # Debug log
                return redirect('admin_dashboard')
            print(f"DEBUG LOGIN: Redirecting to home")  # Debug log
            return redirect('home')
        else:
            print(f"DEBUG LOGIN: Invalid credentials")  # Debug log
            return render(request, 'login.html', {
                'error': 'Invalid email or password. Please try again.',
                'values': {'email': email}
            })


# =============================================================================
# AUTHENTICATION: SIGNOUT
# =============================================================================
def signout(request):
    """Logout and clear session."""
    request.session.clear()
    return redirect('login')


def signout1(request):
    """Logout and redirect to home."""
    request.session.clear()
    return redirect('home')


# =============================================================================
# CART VIEWS
# =============================================================================
@login_required_custom
def cart(request):
    """Display cart items with product details. Pre-calculates all totals in view."""
    if request.method == 'GET':
        if 'cart' not in request.session:
            request.session['cart'] = {}

        ids = list(request.session['cart'].keys())
        if ids:
            prod = Std.get_product_by_id(ids)
        else:
            prod = []

        # Calculate all totals in view (Bug 11 fix)
        cart = request.session.get('cart', {})
        cart_items = []
        total = 0

        for item in prod:
            qty = cart.get(str(item.id), 0)
            line_total = item.price * qty
            total += line_total
            cart_items.append({
                'product': item,
                'quantity': qty,
                'line_total': line_total,
            })

        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'prod': prod,
            'cart': cart,
            'subtotal': total,
            'total': total,
            'cart_count': sum(cart.values()) if cart else 0,
        })

    return redirect('cart')


@login_required_custom
def update_cart_item(request):
    """AJAX POST to update cart item quantity without page reload."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        if not product_id or not quantity:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters.'})

        try:
            quantity = int(quantity)
            if quantity < 1:
                return JsonResponse({'status': 'error', 'message': 'Quantity must be at least 1.'})
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid quantity.'})

        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] = quantity
            request.session['cart'] = cart

            # Get product for price calculation
            try:
                product = Std.objects.get(id=product_id)
                item_total = product.price * quantity
            except Std.DoesNotExist:
                item_total = 0

            cart_total = 0
            for pid, qty in cart.items():
                try:
                    p = Std.objects.get(id=pid)
                    cart_total += p.price * qty
                except Std.DoesNotExist:
                    pass

            return JsonResponse({
                'status': 'success',
                'item_total': item_total,
                'cart_total': cart_total,
                'cart_count': sum(cart.values())
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Item not in cart.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


@login_required_custom
def remove_cart_item(request):
    """AJAX POST to remove item from cart."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'Missing product ID.'})

        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart.pop(str(product_id))
            request.session['cart'] = cart

            # Recalculate total
            cart_total = 0
            for pid, qty in cart.items():
                try:
                    p = Std.objects.get(id=pid)
                    cart_total += p.price * qty
                except Std.DoesNotExist:
                    pass

            return JsonResponse({
                'status': 'success',
                'cart_total': cart_total,
                'cart_count': sum(cart.values())
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Item not in cart.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


# =============================================================================
# CHECKOUT
# =============================================================================
@login_required_custom
def checkout(request):
    """Place orders from cart. Uses get_or_create to prevent DoesNotExist crash."""
    if request.method == 'POST':
        address = request.POST.get('address')
        phoneno = request.POST.get('phone')
        Price = request.POST.get('Price', 0)

        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')

        products = Std.get_product_by_id(list(cart.keys()))

        customer_id = request.session.get('customer_id')
        customer_instance, created = Customer.objects.get_or_create(id=customer_id)

        # Calculate estimated delivery (7 days from now)
        estimated_delivery = timezone.now().date() + datetime.timedelta(days=7)

        # Generate tracking number
        tracking_base = f"ERA{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Iterate through products and place orders
        for product in products:
            quantity = cart.get(str(product.id))
            if quantity:
                order = Order(
                    customer=customer_instance,
                    product=product,
                    price=product.price,
                    quantity=quantity,
                    address=address,
                    Phone_no=phoneno,
                    tracking_number=f"{tracking_base}-{product.id}",
                    estimated_delivery=estimated_delivery
                )
                order.place_order()

        # Clear the cart after placing all orders
        request.session['cart'] = {}
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order')

    # GET request: render checkout page
    if 'cart' not in request.session:
        request.session['cart'] = {}

    ids = list(request.session['cart'].keys())
    if ids:
        prod = Std.get_product_by_id(ids)
    else:
        prod = []

    cart = request.session.get('cart', {})
    total = 0
    for item in prod:
        qty = cart.get(str(item.id), 0)
        total += item.price * qty

    # Check for coupon
    coupon_discount = 0
    coupon_code = request.session.get('coupon_code', '')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            if coupon.is_valid(total):
                coupon_discount = int(total * coupon.discount_percent / 100)
        except Coupon.DoesNotExist:
            pass

    customer_id = request.session.get('customer_id')
    customer_instance, _ = Customer.objects.get_or_create(id=customer_id)

    return render(request, 'checkout.html', {
        'prod': prod,
        'cart': cart,
        'total': total,
        'coupon_discount': coupon_discount,
        'final_total': total - coupon_discount,
        'customer': customer_instance
    })


# =============================================================================
# APPLY COUPON
# =============================================================================
@login_required_custom
def apply_coupon(request):
    """AJAX POST to apply coupon code. Returns JSON response."""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        cart_total = request.POST.get('cart_total', 0)

        if not code:
            return JsonResponse({'status': 'error', 'message': 'Please enter a coupon code.'})

        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True)
            if coupon.is_valid(float(cart_total)):
                request.session['coupon_code'] = coupon.code
                discount = int(float(cart_total) * coupon.discount_percent / 100)
                return JsonResponse({
                    'status': 'success',
                    'message': f'Coupon applied! {coupon.discount_percent}% discount.',
                    'discount': discount,
                    'final_total': float(cart_total) - discount
                })
            else:
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']
                return JsonResponse({'status': 'error', 'message': 'Coupon is not valid for this order amount or has expired.'})
        except Coupon.DoesNotExist:
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
            return JsonResponse({'status': 'error', 'message': 'Invalid coupon code.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


# =============================================================================
# ORDER HISTORY (CUSTOMER)
# =============================================================================
@login_required_custom
def order(request):
    """Customer's order history. Pre-calculates totals."""
    if request.method == 'GET':
        customer_id = request.session.get('customer_id')
        orders = Order.get_order_by_customer(customer_id).order_by('-date')

        # Pre-calculate order totals (Bug 12 fix)
        orders_with_totals = []
        for order in orders:
            order.order_total = order.price * order.quantity
            orders_with_totals.append(order)

        return render(request, 'order.html', {'orders': orders_with_totals})


# =============================================================================
# CANCEL ORDER (CUSTOMER)
# =============================================================================
@login_required_custom
def cancel_order(request, order_id):
    """Customer can cancel their pending order."""
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        order = get_object_or_404(Order, id=order_id, customer_id=customer_id)

        if order.status in ('Pending', 'Processing'):
            order.status = 'Cancelled'
            order.save()
            messages.success(request, f'Order #{order.id} has been cancelled.')
        else:
            messages.error(request, 'This order cannot be cancelled as it is already being processed or shipped.')

        return redirect('order')

    return redirect('order')


# =============================================================================
# PROFILE
# =============================================================================
@login_required_custom
def profile(request):
    """Customer profile page showing info, order history, and password change."""
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)

    # Order history
    orders = Order.get_order_by_customer(customer_id).order_by('-date')[:5]

    # Order stats
    order_stats = Order.get_order_by_customer(customer_id).aggregate(
        total_orders=Count('id'),
        total_spent=Sum('price'),
        pending=Count('id', filter=Q(status='Pending')),
        delivered=Count('id', filter=Q(status='Delivered')),
    )

    if request.method == 'POST' and 'update_profile' in request.POST:
        # Update profile info
        customer.fname = request.POST.get('fname', customer.fname)
        customer.lname = request.POST.get('lname', customer.lname)
        customer.phone = request.POST.get('phone', customer.phone)
        if request.FILES.get('profile_picture'):
            customer.profile_picture = request.FILES['profile_picture']
        customer.save()
        request.session['customer_email'] = customer.email
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    if request.method == 'POST' and 'change_password' in request.POST:
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if customer.password != current_password:
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif not new_password or len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            customer.password = new_password
            customer.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')

    return render(request, 'profile.html', {
        'customer': customer,
        'orders': orders,
        'order_stats': order_stats
    })


# =============================================================================
# WISHLIST VIEWS (Bug 10)
# =============================================================================
@login_required_custom
def add_to_wishlist(request, product_id):
    """Add product to wishlist. Supports both regular and AJAX requests."""
    customer_id = request.session.get('customer_id')
    product = get_object_or_404(Std, id=product_id, is_active=True)

    try:
        Wishlist.objects.get_or_create(customer_id=customer_id, product=product)
        message = f'{product.name} added to wishlist!'
        messages.success(request, message)
    except IntegrityError:
        message = f'{product.name} is already in your wishlist.'
        messages.info(request, message)

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': message})

    return redirect('product_detail', product_id=product_id)


@login_required_custom
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist. Supports both regular and AJAX requests."""
    customer_id = request.session.get('customer_id')

    try:
        wishlist_item = Wishlist.objects.get(customer_id=customer_id, product_id=product_id)
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        message = f'{product_name} removed from wishlist.'
        messages.success(request, message)
    except Wishlist.DoesNotExist:
        message = 'Item not found in wishlist.'
        messages.error(request, message)

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': message})

    # If redirecting back from product detail, go there
    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('wishlist')


@login_required_custom
def view_wishlist(request):
    """View all wishlist items."""
    customer_id = request.session.get('customer_id')
    wishlist_items = Wishlist.objects.filter(customer_id=customer_id).select_related('product')

    # Calculate cart count
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0

    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items,
        'cart_count': cart_count,
    })


# =============================================================================
# TOGGLE WISHLIST (AJAX)
# =============================================================================
@login_required_custom
def toggle_wishlist(request, product_id):
    """Toggle wishlist status via AJAX. Add if not present, remove if present."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        customer_id = request.session.get('customer_id')
        product = get_object_or_404(Std, id=product_id, is_active=True)

        try:
            wishlist_item = Wishlist.objects.get(customer_id=customer_id, product=product)
            wishlist_item.delete()
            action = 'removed'
            message = f'{product.name} removed from wishlist.'
            in_wishlist = False
        except Wishlist.DoesNotExist:
            Wishlist.objects.create(customer_id=customer_id, product=product)
            action = 'added'
            message = f'{product.name} added to wishlist!'
            in_wishlist = True

        return JsonResponse({
            'status': 'success',
            'action': action,
            'message': message,
            'in_wishlist': in_wishlist
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


# =============================================================================
# NEWSLETTER SIGNUP
# =============================================================================
def newsletter_signup(request):
    """POST form in footer for newsletter subscription."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please enter your email address.')
        else:
            try:
                Newsletter.objects.get_or_create(email=email)
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            except IntegrityError:
                messages.info(request, 'You are already subscribed to our newsletter.')

        # Redirect back to the page the user came from
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    return redirect('home')


# =============================================================================
# ADMIN DASHBOARD
# =============================================================================
def admin_dashboard(request):
    """Admin dashboard with sales stats, top products, and chart data."""
    # Check authentication
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
        messages.error(request, 'Admin access required.')
        return redirect('login')

    # Date range for stats (last 30 days)
    thirty_days_ago = timezone.now().date() - datetime.timedelta(days=30)

    # Sales statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='Delivered').aggregate(total=Sum('price'))['total'] or 0
    pending_orders = Order.objects.filter(status='Pending').count()
    processing_orders = Order.objects.filter(status='Processing').count()
    shipped_orders = Order.objects.filter(status='Shipped').count()
    delivered_orders = Order.objects.filter(status='Delivered').count()
    cancelled_orders = Order.objects.filter(status='Cancelled').count()

    # Revenue for last 30 days
    recent_revenue = Order.objects.filter(
        date__gte=thirty_days_ago,
        status__in=['Delivered', 'Shipped']
    ).aggregate(total=Sum('price'))['total'] or 0

    # Total customers
    total_customers = Customer.objects.count()

    # Top products by quantity sold
    top_products = Order.objects.filter(
        status__in=['Delivered', 'Shipped', 'Processing']
    ).values(
        'product__id',
        'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_sold')[:10]

    # Orders by status (for pie chart)
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')

    # Revenue by day (last 30 days, for line chart)
    revenue_by_day = Order.objects.filter(
        date__gte=thirty_days_ago,
        status__in=['Delivered', 'Shipped']
    ).extra(select={'day': 'date'}).values('day').annotate(
        revenue=Sum('price'),
        orders=Count('id')
    ).order_by('day')

    # Recent orders
    recent_orders = Order.objects.select_related(
        'customer', 'product'
    ).order_by('-date', '-id')[:15]

    # Top categories
    top_categories = Cat.objects.annotate(
        product_count=Count('std'),
        order_count=Count('std__order')
    ).order_by('-order_count')[:5]

    # Low stock products
    low_stock_products = Std.objects.filter(
        stock_quantity__lte=10,
        is_active=True
    ).order_by('stock_quantity')[:10]

    context = {
        'today_orders': total_orders,
        'today_revenue': total_revenue,
        'total_products': Std.objects.count(),
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'category_sales': top_categories,
        'low_stock_products': low_stock_products,
        'orders_by_status': list(orders_by_status),
        'chart_labels': [str(day['day']) for day in revenue_by_day],
        'chart_data': [float(day['revenue']) for day in revenue_by_day],
        'is_admin': is_admin,
    }

    return render(request, 'dashboard.html', context)


# =============================================================================
# ADMIN: UPDATE ORDER STATUS
# =============================================================================
@staff_member_required
def update_order_status(request):
    """Admin can update order status via AJAX."""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        if not order_id or not new_status:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters.'})

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'status': 'error', 'message': 'Invalid status.'})

        try:
            order = Order.objects.get(id=order_id)
            old_status = order.status
            order.status = new_status
            order.save()

            # Auto-generate tracking number if status is Shipped
            if new_status == 'Shipped' and not order.tracking_number:
                order.tracking_number = f"ERA{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{order.product.id}"
                order.estimated_delivery = timezone.now().date() + datetime.timedelta(days=7)
                order.save()

            return JsonResponse({
                'status': 'success',
                'message': f'Order #{order_id} status updated from {old_status} to {new_status}.'
            })
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


# =============================================================================
# ADMIN: EXPORT ORDERS TO CSV
# =============================================================================
@staff_member_required
def export_orders_csv(request):
    """Export orders to CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="orders_{datetime.date.today().isoformat()}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Order ID',
        'Customer Name',
        'Customer Email',
        'Product',
        'Quantity',
        'Price',
        'Total',
        'Status',
        'Address',
        'Phone',
        'Order Date',
        'Tracking Number',
        'Estimated Delivery',
    ])

    orders = Order.objects.select_related('customer', 'product').all().order_by('-date')

    for order in orders:
        writer.writerow([
            order.id,
            f'{order.customer.fname} {order.customer.lname}',
            order.customer.email,
            order.product.name,
            order.quantity,
            order.price,
            order.price * order.quantity,
            order.status,
            order.address,
            order.Phone_no,
            order.date,
            order.tracking_number or 'N/A',
            order.estimated_delivery or 'N/A',
        ])

    return response


# =============================================================================
# CATEGORY MANAGEMENT (Admin)
# =============================================================================
from .form import CatForm


def addcat(request):
    """Add new category."""
    if request.method == 'POST':
        form = CatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CatForm()
    return render(request, 'addcat.html', {'form': form})


def listcat(request):
    """List all categories."""
    categories = Cat.objects.all()
    return render(request, 'listcat.html', {'categories': categories})


def deletecat(request, id):
    """Delete a category."""
    remove = get_object_or_404(Cat, id=id)
    remove.delete()
    return redirect('home')


def editcat(request, id):
    """Edit a category."""
    edit = get_object_or_404(Cat, id=id)
    if request.method == 'POST':
        form = CatForm(request.POST, instance=edit)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CatForm(instance=edit)

    content = {'form': form}
    return render(request, 'editcat.html', content)


# =============================================================================
# PRODUCT MANAGEMENT (Admin)
# =============================================================================
from .form import ProductForm


def addpro(request):
    """Add new product with support for file upload or URL image."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)

            # If image_url is provided and no file was uploaded, download the image
            image_url = form.cleaned_data.get('image_url')
            if image_url and not request.FILES.get('image'):
                success, message = product.download_image_from_url()
                if success:
                    product.save()
                    messages.success(request, f'Product added successfully! Image downloaded from URL.')
                else:
                    messages.error(request, f'Product saved but image download failed: {message}')
                    product.save()
            else:
                product.save()
                messages.success(request, 'Product added successfully!')

            return redirect('home')
        else:
            # Form has errors, display them
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    return render(request, 'addpro.html', {'form': form})


def listpro(request):
    """List all products."""
    products = Std.objects.all()
    return render(request, 'listpro.html', {'products': products})


def deletepro(request, id):
    """Delete a product."""
    product = get_object_or_404(Std, id=id)
    product.delete()
    return redirect('listpro')


def editpro(request, id):
    """Edit a product with support for file upload or URL image."""
    product = get_object_or_404(Std, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)

            # If image_url is provided and no file was uploaded, download the image
            image_url = form.cleaned_data.get('image_url')
            if image_url and not request.FILES.get('image'):
                # Only download if the URL changed or no image exists
                if image_url != product.image_url or not product.image:
                    success, message = product.download_image_from_url()
                    if success:
                        product.save()
                        messages.success(request, f'Product updated successfully! Image downloaded from URL.')
                    else:
                        messages.error(request, f'Product saved but image download failed: {message}')
                        product.save()
                else:
                    product.save()
                    messages.success(request, 'Product updated successfully!')
            else:
                product.save()
                messages.success(request, 'Product updated successfully!')

            return redirect('listpro')
        else:
            # Form has errors, display them
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)

    return render(request, 'editpro.html', {'form': form})


# =============================================================================
# ORDER MANAGEMENT (Admin)
# =============================================================================
def finalorder(request):
    """Admin order list."""
    orders = Order.objects.select_related('customer', 'product').all().order_by('-date')

    # Allow filtering
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'finalorder.html', {'orders': orders})


from .form import OrderForm


def edit_order(request, order_id):
    """Edit an order."""
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('finalorder')
    else:
        form = OrderForm(instance=order)

    return render(request, 'edit_order.html', {'form': form})
