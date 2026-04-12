# E-commerce Views - New System (Django User-based)
# These views complement the existing views.py functionality

from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.views.decorators.http import require_POST
import datetime

from .models import (
    Category, Product, OrderNew, OrderItem, CartNew, CartItemNew, Review,
    Std, Cat, Customer, Order, Rating, Wishlist
)
from .form import (
    NewProductForm, NewCategoryForm, CheckoutForm, ProfileForm, ReviewForm, ContactForm
)


# =============================================================================
# STAFF MEMBER REQUIRED DECORATOR
# =============================================================================
def staff_member_required(view_func):
    """Decorator to check if logged-in user is staff (admin)."""
    from functools import wraps
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# =============================================================================
# NEW CART VIEWS (Django User-based)
# =============================================================================
@login_required
def cart_view(request):
    """Display cart with Django User-based cart."""
    cart, _ = CartNew.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    subtotal = sum(item.get_total() for item in items)
    shipping = 0 if subtotal >= 200 else 15
    total = subtotal + shipping

    return render(request, 'cart.html', {
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'free_delivery_remaining': max(0, 200 - float(subtotal))
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
    else:
        item.quantity = 1
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
        messages.success(request, 'Cart updated.')
    else:
        item.delete()
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# =============================================================================
# NEW CHECKOUT VIEW
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
            address += f", {form.cleaned_data['city']}, {form.cleaned_data['state']} {form.cleaned_data['zip_code']}, {form.cleaned_data['country']}"

            # Generate tracking number
            tracking_number = f"ERA{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            estimated_delivery = timezone.now().date() + datetime.timedelta(days=7)

            order = OrderNew.objects.create(
                user=request.user,
                total_amount=total,
                shipping_address=address,
                tracking_number=tracking_number,
                estimated_delivery=estimated_delivery
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.discount_price or item.product.price
                )
                # Reduce stock
                item.product.stock -= item.quantity
                item.product.save()

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


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page."""
    order = get_object_or_404(OrderNew, id=order_id, user=request.user)
    items = order.items.select_related('product').all()
    return render(request, 'order_confirmation.html', {
        'order': order,
        'items': items
    })


@login_required
def my_orders(request):
    """User's order history."""
    orders = OrderNew.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


# =============================================================================
# NEW PRODUCT DETAIL VIEW
# =============================================================================
def product_detail_new(request, slug):
    """Product detail page with new models."""
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.select_related('user').all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()

    # Check if user has reviewed
    user_review = None
    user_has_reviewed = False
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(product=product, user=request.user)
            user_has_reviewed = True
        except Review.DoesNotExist:
            pass

    # Related products
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    # Check wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            customer__email=request.user.email,
            product_id=product.id  # Using Std product ID mapping would be needed
        ).exists()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'user_review': user_review,
        'user_has_reviewed': user_has_reviewed,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'product_detail_new.html', context)


@login_required
@require_POST
def submit_review(request, product_id):
    """Submit product review."""
    product = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '').strip()

    if not rating or not comment:
        messages.error(request, 'Please provide a rating and comment.')
        return redirect('product_detail_new', slug=product.slug)

    review, created = Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={'rating': rating, 'comment': comment}
    )

    if created:
        messages.success(request, 'Thank you for your review!')
    else:
        messages.success(request, 'Your review has been updated!')

    return redirect('product_detail_new', slug=product.slug)


# =============================================================================
# SHOP VIEW (New Models)
# =============================================================================
def shop_view(request):
    """Shop page with filtering and search for new Product model."""
    categories = Category.objects.all()
    cat_slug = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', '-created_at')

    products = Product.objects.all()

    if cat_slug:
        products = products.filter(category__slug=cat_slug)

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

    valid_sort_fields = ['price', '-price', 'name', '-name', 'created_at', '-created_at']
    if sort_by in valid_sort_fields:
        products = products.order_by(sort_by)
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    return render(request, 'shopping.html', {
        'products': products_page,
        'categories': categories,
        'current_category': cat_slug,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })


# =============================================================================
# AUTH VIEWS (Django User-based)
# =============================================================================
def login_view(request):
    """Django User login view."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            return render(request, 'login.html', {'error': 'Please enter both email and password.'})

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                django_login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid email or password.'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email or password.'})

    return render(request, 'login.html')


@login_required
def logout_view(request):
    """Django User logout."""
    django_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def register_view(request):
    """Django User registration."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not all([first_name, last_name, email, username, password, confirm_password]):
            return render(request, 'register.html', {'error': 'All fields are required.'})

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered.'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken.'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')

    return render(request, 'register.html')


@login_required
def profile_view(request):
    """User profile page."""
    orders = OrderNew.objects.filter(user=request.user).order_by('-created_at')[:5]

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

    return render(request, 'profile.html', {
        'form': form,
        'orders': orders
    })


# =============================================================================
# STATIC PAGES
# =============================================================================
def home_view(request):
    """Home page."""
    featured_products = Product.objects.filter(is_featured=True)[:8]
    new_products = Product.objects.filter(is_new=True)[:8]
    categories = Category.objects.all()[:6]
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
    })


def about_view(request):
    """About page."""
    return render(request, 'about.html')


def contact_view(request):
    """Contact page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, f"Thank you {form.cleaned_data['name']}! Your message has been received.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# =============================================================================
# ADMIN VIEWS
# =============================================================================
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with stats and charts."""
    thirty_days_ago = timezone.now().date() - datetime.timedelta(days=30)

    total_orders = OrderNew.objects.count()
    total_revenue = OrderNew.objects.filter(status__in=['delivered', 'shipped']).aggregate(total=Sum('total_amount'))['total'] or 0
    pending_orders = OrderNew.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_active=True).count()

    # Low stock items
    low_stock = Product.objects.filter(stock__lt=5, stock__gt=0).order_by('stock')[:10]

    # Orders by status
    orders_by_status = OrderNew.objects.values('status').annotate(count=Count('id'))

    # Revenue by month (last 6 months)
    revenue_by_month = []
    for i in range(5, -1, -1):
        month = timezone.now() - datetime.timedelta(days=30*i)
        month_orders = OrderNew.objects.filter(
            created_at__month=month.month,
            created_at__year=month.year,
            status__in=['delivered', 'shipped']
        )
        revenue = month_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_by_month.append({
            'month': month.strftime('%b %Y'),
            'revenue': float(revenue)
        })

    # Top products
    top_products = OrderItem.objects.values(
        'product__id', 'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_sold')[:5]

    # Recent orders
    recent_orders = OrderNew.objects.select_related('user').order_by('-created_at')[:10]

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'low_stock': low_stock,
        'orders_by_status': list(orders_by_status),
        'revenue_by_month': revenue_by_month,
        'top_products': top_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin/dashboard.html', context)


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
    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    categories = Category.objects.all()
    return render(request, 'admin/list_products.html', {
        'products': products_page,
        'categories': categories,
        'search_query': search_query,
    })


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


@staff_member_required
@require_POST
def delete_category(request, pk):
    """Delete category."""
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('list_categories')


@staff_member_required
def list_categories(request):
    """List all categories."""
    categories = Category.objects.all().annotate(product_count=Count('products'))
    return render(request, 'admin/list_categories.html', {'categories': categories})


@staff_member_required
def admin_orders(request):
    """View all orders with status filter."""
    orders = OrderNew.objects.select_related('user').all().order_by('-created_at')
    status_filter = request.GET.get('status', '')

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'admin/orders.html', {
        'orders': orders,
        'status_filter': status_filter,
    })


@staff_member_required
def order_detail_admin(request, order_id):
    """View order details and update status."""
    order = get_object_or_404(OrderNew, pk=order_id)
    items = order.items.select_related('product').all()

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(OrderNew.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}.')
            return redirect('order_detail_admin', order_id=order.id)

    return render(request, 'admin/order_detail.html', {
        'order': order,
        'items': items,
    })


@staff_member_required
def admin_customers(request):
    """View all customers."""
    customers = User.objects.filter(is_active=True).order_by('-date_joined')
    search_query = request.GET.get('q', '').strip()

    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query)
        )

    # Annotate with order stats
    customers = customers.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    )

    return render(request, 'admin/customers.html', {
        'customers': customers,
        'search_query': search_query,
    })


# =============================================================================
# WISHLIST VIEWS (Django User-based via email mapping)
# =============================================================================
@login_required
def view_wishlist(request):
    """View user's wishlist."""
    # Map Django User to Customer via email
    customer = Customer.objects.filter(email=request.user.email).first()
    items = []
    if customer:
        items = Wishlist.objects.filter(customer=customer).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': items})


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    customer = Customer.objects.filter(email=request.user.email).first()
    if not customer:
        messages.error(request, 'Please set up your profile first.')
        return redirect('profile')

    product = get_object_or_404(Std, id=product_id)
    _, created = Wishlist.objects.get_or_create(customer=customer, product=product)
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'shopping'))


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    customer = Customer.objects.filter(email=request.user.email).first()
    if customer:
        Wishlist.objects.filter(customer=customer, product_id=product_id).delete()
        messages.success(request, 'Item removed from wishlist.')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('wishlist')


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    """Toggle product in wishlist (add/remove)."""
    customer = Customer.objects.filter(email=request.user.email).first()
    if not customer:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Profile not set up.'})
        return redirect('profile')

    product = get_object_or_404(Std, id=product_id)
    item, created = Wishlist.objects.get_or_create(customer=customer, product=product)
    if created:
        action = 'added'
        message = f'{product.name} added to wishlist!'
    else:
        item.delete()
        action = 'removed'
        message = f'{product.name} removed from wishlist.'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'action': action, 'message': message})
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'shopping'))
