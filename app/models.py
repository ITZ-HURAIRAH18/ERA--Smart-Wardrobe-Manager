from django.db import models
import datetime
# Category model
class Cat(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_pro():
        return Cat.objects.all()  # Get all categories



   


# Product model (Std model)
class Std(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Cat, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to="images/", default="images/default.jpg")

    def __str__(self):
        return self.name
    @staticmethod
    def get_product_by_id(ids):
        return Std.objects.filter(id__in=ids)  #due to list Filter products by category ID
       

    @staticmethod
    def get_all_pro():
        return Std.objects.all()  # Get all products

    @staticmethod
    def get_all_pro_by_category(cat_id):
        if cat_id:
            return Std.objects.filter(category_id=cat_id)  # Filter products by category ID
        else:
            return Std.objects.all()  # If no category is specified, return all products

class Customer(models.Model):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.CharField(max_length=255)
       
    def __str__(self):
         return self.fname + ' ' + self.lname 
    def reg(self):
        self.save()  # Save the customer to the database

    def is_exit(self):
        """Check if the customer already exists by email"""
        return Customer.objects.filter(email=self.email).exists()

    @staticmethod
    def get_customer_by_email(email):
        """Get customer by email"""
        try:
          return Customer.objects.filter(email=email).first()  # Use .first() to return a single customer
        except:
            return False
        

import datetime
from django.db import models

class Order(models.Model):
    product = models.ForeignKey(Std, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    address = models.CharField(max_length=50, default="")
    Phone_no = models.CharField(max_length=50, default="")
    Price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
         return self.customer.fname + ' ' + self.customer.lname

    # Make place_order an instance method, not static
    def place_order(self):
        self.save()  # This saves the current order instance
    @staticmethod
    def get_order_by_customer(customer_id): 
        return Order.objects.filter(customer=customer_id)