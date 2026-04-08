# ERA Cart Template Tags
from django import template

register = template.Library()


@register.filter(name='cart_quantity')
def cart_quantity(product, cart):
    """Get quantity of a product in cart."""
    keys = cart.keys()
    for id in keys:
        if int(id) == product.id:
            return cart.get(id)
    return 0


@register.filter(name='price_total')
def price_total(product, cart):
    """Calculate total price for a product in cart."""
    return product.price * cart_quantity(product, cart)


@register.filter(name='cart_price_total')
def cart_price_total(products, cart):
    """Calculate total price for all products in cart."""
    total = 0
    for p in products:
        total += p.price * cart_quantity(p, cart)
    return total


@register.filter(name='currency')
def currency(number):
    """Format number as currency."""
    return "$ " + str(number)


@register.filter(name='multiply')
def multiply(number, num1):
    """Multiply two numbers."""
    return number * num1


@register.filter(name='format_price')
def format_price(number):
    """Format price with 2 decimal places."""
    try:
        return f"${float(number):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@register.filter(name='status_class')
def status_class(status):
    """Convert status to CSS class name."""
    return status.lower().replace(' ', '-')


@register.filter(name='dict_get')
def dict_get(dictionary, key):
    """Get value from dictionary by key."""
    try:
        return dictionary.get(key, 0)
    except AttributeError:
        return 0
