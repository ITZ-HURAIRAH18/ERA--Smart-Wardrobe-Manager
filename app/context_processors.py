from .models import CartItem, Customer, Cat, Category, CartNew, Std


def cart_count(request):
    """Context processor to provide cart count in all templates.
    Supports both session-based and Django User-based carts.
    Counts items from BOTH session cart and CartNew for accurate display.
    """
    count = 0

    # Always check session cart first (for anonymous users and session-based items)
    session_cart = request.session.get('cart', {})
    if session_cart:
        count += sum(session_cart.values())

    # If user is authenticated, also count CartNew items
    if request.user.is_authenticated:
        try:
            cart_new = CartNew.objects.get(user=request.user)
            count += cart_new.items_count()
        except CartNew.DoesNotExist:
            pass

    return {'cart_count': count}


def categories_all(request):
    """Context processor to provide all categories for dropdown.
    Merges both old Cat and new Category models.
    """
    # Get new Category model items
    new_categories = list(Category.objects.all().order_by('name'))

    # Get old Cat model items (backward compatibility)
    old_categories = list(Cat.objects.all().order_by('name'))

    # Return combined list, preferring new Category model
    return {
        'categories_all': new_categories if new_categories else old_categories,
        'all_categories': new_categories if new_categories else old_categories,
    }
