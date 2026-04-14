import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# =============================================================================
# EXISTING MODELS (kept for backward compatibility)
# =============================================================================

class Cat(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_pro():
        return Cat.objects.all()


class Std(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Cat, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to="images/", default="images/default.jpg")

    # New fields for inventory and variants
    available_sizes = models.CharField(max_length=50, default="S,M,L,XL", help_text="Comma-separated sizes e.g. S,M,L,XL")
    available_colors = models.CharField(max_length=200, default="Red,Blue,Black", help_text="Comma-separated colors e.g. Red,Blue,Black")
    stock_quantity = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_product_by_id(ids):
        return Std.objects.filter(id__in=ids)

    @staticmethod
    def get_all_pro():
        return Std.objects.all()

    @staticmethod
    def get_all_pro_by_category(cat_id):
        if cat_id:
            return Std.objects.filter(category_id=cat_id)
        else:
            return Std.objects.all()

    def is_new(self):
        """Check if product was added in the last 7 days"""
        now = datetime.datetime.now(datetime.timezone.utc)
        return (now - self.created_at).days <= 7

    @property
    def avg_rating(self):
        """Calculate average rating for this product."""
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.stars for r in ratings) / ratings.count(), 1)
        return 0


class Customer(models.Model):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg", blank=True, null=True)

    def __str__(self):
        return self.fname + ' ' + self.lname

    def reg(self):
        self.save()

    def is_exit(self):
        """Check if the customer already exists by email"""
        return Customer.objects.filter(email=self.email).exists()

    @staticmethod
    def get_customer_by_email(email):
        """Get customer by email"""
        try:
            return Customer.objects.filter(email=email).first()
        except Exception:
            return False


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    product = models.ForeignKey(Std, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    address = models.CharField(max_length=255, default="")
    Phone_no = models.CharField(max_length=50, default="")
    date = models.DateField(default=datetime.datetime.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    tracking_number = models.CharField(max_length=100, blank=True, default="")
    estimated_delivery = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.customer.fname + ' ' + self.customer.lname

    def place_order(self):
        self.save()

    @staticmethod
    def get_order_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id)

    @property
    def total_price(self):
        """Calculate total price for this order."""
        return self.price * self.quantity


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.customer.fname}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Std, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    selected_size = models.CharField(max_length=20, default="")
    selected_color = models.CharField(max_length=50, default="")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Rating(models.Model):
    product = models.ForeignKey(Std, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    review = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'customer')

    def __str__(self):
        return f"{self.customer.fname} - {self.product.name} - {self.stars} stars"


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Std, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.customer.fname}'s wishlist - {self.product.name}"

    def get_product_image(self):
        """Get product image URL for template convenience."""
        return self.product.image.url if self.product.image else ''


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField()
    active = models.BooleanField(default=True)
    expiry_date = models.DateField()
    min_order_value = models.IntegerField(default=0)

    def __str__(self):
        return self.code

    def is_valid(self, cart_total):
        """Check if coupon is valid"""
        if not self.active:
            return False
        if datetime.date.today() > self.expiry_date:
            return False
        if cart_total < self.min_order_value:
            return False
        return True


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# =============================================================================
# NEW E-COMMERCE MODELS (per prompt.txt specification)
# These use Django's User model for proper auth integration
# =============================================================================

class Category(models.Model):
    """Product category with slug and image."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/shopping/?category={self.slug}"

    def product_count(self):
        return self.products.count()


class Product(models.Model):
    """Product with pricing, inventory, and media."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    stock = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail_new', kwargs={'slug': self.slug})

    def get_discount_percentage(self):
        if self.discount_price and self.discount_price < self.price:
            return int((1 - self.discount_price / self.price) * 100)
        return 0

    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    def is_in_stock(self):
        return self.stock > 0


class OrderNew(models.Model):
    """Order using Django User model with proper status tracking."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Pay on Delivery'),
        ('card', 'Credit/Debit Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, default="")
    estimated_delivery = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.get_full_name() or self.user.username}"

    def get_items_count(self):
        return self.items.count()


class OrderItem(models.Model):
    """Individual item within an order."""
    order = models.ForeignKey(OrderNew, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255, default='')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name or self.product.name} x {self.quantity}"

    def get_total(self):
        return self.price * self.quantity


class CartNew(models.Model):
    """Shopping cart linked to Django User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart_new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.get_full_name() or self.user.username}"

    def items_count(self):
        return sum(item.quantity for item in self.items.all())

    def get_subtotal(self):
        return sum(item.get_total() for item in self.items.all())


class CartItemNew(models.Model):
    """Individual item within a cart."""
    cart = models.ForeignKey(CartNew, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    selected_size = models.CharField(max_length=20, default="")
    selected_color = models.CharField(max_length=50, default="")

    class Meta:
        unique_together = ('cart', 'product', 'selected_size', 'selected_color')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        price = self.product.discount_price or self.product.price
        return price * self.quantity


class Review(models.Model):
    """Product review with rating and comment."""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified_purchase = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"

    def get_average_rating(self):
        return self.rating
