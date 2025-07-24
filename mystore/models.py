import datetime
from email.policy import default
from django.db import models
from django.contrib.auth.models import User
#Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username
class Category(models.Model):
    x = (
        ('clothes', 'clothes'),
        ('kitchin', 'kitchin'),
        ('food', 'food'),
        ('elctronic', 'elctronic'),
    )
    name = models.CharField(choices=x, max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=60)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    quantitystock=models.IntegerField(default=0)
    description = models.CharField(
        max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='product_photo')

    def __str__(self):
        return self.name
    class Meta:
        indexes=[
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, default='', blank=True)
    phone = models.CharField(max_length=50, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    total_price_order=models.IntegerField(default=0)
    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"