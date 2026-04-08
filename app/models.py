import datetime
import uuid
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from django.db import models
from django.contrib.auth.models import User


# Category model
class Cat(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_pro():
        return Cat.objects.all()


# Product model
class Std(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Cat, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to="images/", default="images/default.jpg")
    image_url = models.URLField(blank=True, null=True, help_text="External image URL (optional)")

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

    def get_image_url(self):
        """Return the appropriate image URL.

        Priority:
        1. Uploaded image (image field)
        2. External URL (image_url field)
        3. Default image path
        """
        if self.image and hasattr(self.image, 'url') and self.image.url:
            return self.image.url
        if self.image_url:
            return self.image_url
        # Return the default image path
        return settings.MEDIA_URL + 'images/default.jpg' if settings.MEDIA_URL else '/media/images/default.jpg'

    def download_image_from_url(self, timeout=10):
        """Download an image from the image_url field and save it to the image field.

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.image_url:
            return False, "No URL provided."

        # Validate URL format
        url_validator = URLValidator()
        try:
            url_validator(self.image_url)
        except Exception:
            return False, "Invalid URL format."

        # Parse URL to check file extension
        parsed_url = urlparse(self.image_url)
        path = parsed_url.path.lower()
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']

        # Download the image
        try:
            response = requests.get(self.image_url, timeout=timeout, stream=True)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return False, "Download timed out. The server took too long to respond."
        except requests.exceptions.ConnectionError:
            return False, "Connection error. Could not reach the URL."
        except requests.exceptions.RequestException as e:
            return False, f"Download failed: {str(e)}"

        # Check content-type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return False, "URL does not point to an image. Content-type: {}".format(content_type)

        # Determine file extension from content-type or URL path
        ext_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/svg+xml': '.svg',
        }
        ext = ext_map.get(content_type.split(';')[0].strip())

        # Fallback: try to get extension from URL path
        if not ext:
            for valid_ext in valid_extensions:
                if path.endswith(valid_ext):
                    ext = valid_ext
                    break
        if not ext:
            ext = '.jpg'  # Default extension

        # Generate a unique filename
        filename = f"product_{uuid.uuid4().hex}{ext}"

        # Save to the image field
        content = ContentFile(response.content)
        self.image.save(filename, content, save=False)

        return True, "Image downloaded and saved successfully."


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


# Cart and CartItem models
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


# Rating model
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


# Wishlist model
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


# Coupon model
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


# Newsletter model
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
