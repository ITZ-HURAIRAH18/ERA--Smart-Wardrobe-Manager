from .models import CartItem, Customer, Cat


def cart_count(request):
    """Context processor to provide cart count in all templates.
    Uses session-based authentication with Customer model.
    """
    # Session-based cart count
    cart = request.session.get('cart', {})
    count = sum(cart.values()) if cart else 0
    
    return {'cart_count': count}


def categories_all(request):
    """Context processor to provide all categories for mega dropdown"""
    return {'categories_all': Cat.objects.all()}
