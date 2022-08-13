from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator 
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(unique=True, blank=False, null=False, max_length=50)
    avatar = models.ImageField(upload_to='upload/%Y/%m')
    verified = models.BooleanField(default=False)
    
    USER_ROLE = (
        (0, 'Customer'),
        (1, 'Store'),
        (2, 'Admin')
    )
    role = models.IntegerField(choices=USER_ROLE, default=0)

class Category(models.Model):
    name = models.CharField(max_length= 255,unique=True, blank=False, null=False)

class Product(models.Model):
    name = models.CharField(max_length= 255,unique=True, blank=False, null=False)
    is_available = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category)
    sold_amount = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    picture = models.ImageField(upload_to='night_owl/product', null=True)
    description = models.TextField(blank=True, null=True)

class Shipper(models.Model):
    name = models.CharField(max_length=255)

class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateField(null=True)
    order_shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True)

class Option(models.Model):
    unit = models.CharField(max_length=255, blank=False, null=False)
    unit_in_stock = models.BigIntegerField(default=1, null=False, blank=False)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Picture(models.Model):
    image = models.ImageField(upload_to='night_owl/product')
    product_option = models.ForeignKey(Option, on_delete=models.CASCADE)

class OrderDetail(models.Model):
    STATUS_CHOICES = (
        (0, 'Approving'),
        (1, 'Pending'),
        (2, 'Completed'),
        (3, 'Canceled'),
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    shipping_id = models.CharField(max_length=255)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)

class Bill(models.Model):
    value = models.DecimalField(max_digits=20, decimal_places=2,validators=[MinValueValidator(0)], null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    payed = models.BooleanField(default=False, null=False, blank=False)
    order_detail = models.OneToOneField(OrderDetail, on_delete=models.CASCADE)

class Address(models.Model):
    # Using GHN API Address for province_id, district_id, ward_id
    country = models.CharField(max_length=100, default="Viet Nam")
    province_id = models.IntegerField(blank=False, null=False)
    district_id = models.IntegerField(blank=False, null=False)
    ward_id = models.IntegerField(blank=False, null=False)
    street = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)