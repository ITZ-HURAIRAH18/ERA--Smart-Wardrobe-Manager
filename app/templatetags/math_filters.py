from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    """Subtract arg from value. Used for cart calculations."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def add_shipping(subtotal):
    """Add $15 shipping if subtotal is under $200."""
    try:
        subtotal = float(subtotal)
        return subtotal + 15 if subtotal < 200 else subtotal
    except (ValueError, TypeError):
        return subtotal


@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def discount_percent(price, discount_price):
    """Calculate discount percentage."""
    try:
        price = float(price)
        discount_price = float(discount_price)
        if price > 0 and discount_price < price:
            return int((1 - discount_price / price) * 100)
        return 0
    except (ValueError, TypeError):
        return 0


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key. Used for session cart access."""
    if dictionary is None:
        return None
    return dictionary.get(str(key))


@register.filter
def cart_total(cart_dict, products):
    """Calculate total from cart dict and products list."""
    total = 0
    if cart_dict and products:
        for product in products:
            qty = cart_dict.get(str(product.id), 0)
            total += product.price * qty
    return total


@register.filter
def to_int(value):
    """Convert value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


@register.filter
def to_float(value):
    """Convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def is_remote_url(value):
    """Check if value is a remote URL (starts with http)."""
    if value is None:
        return False
    value_str = str(value)
    return value_str.startswith('http://') or value_str.startswith('https://')
