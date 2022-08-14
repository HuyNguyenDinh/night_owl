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

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name

class Address(models.Model):
    # Using GHN API Address for province_id, district_id, ward_id
    country = models.CharField(max_length=100, default="Viet Nam")
    province_id = models.IntegerField(blank=False, null=False)
    district_id = models.IntegerField(blank=False, null=False)
    ward_id = models.IntegerField(blank=False, null=False)
    street = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return str(self.ward_id) + ', ' + str(self.district_id) + ', ' + str(self.province_id) + ', ' + self.country

class Category(models.Model):
    name = models.CharField(max_length= 255,unique=True, blank=False, null=False)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField(max_length= 255,unique=True, blank=False, null=False)
    is_available = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category)
    sold_amount = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    picture = models.ImageField(upload_to='night_owl/product', null=True)
    description = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=20, decimal_places=2, default=1, validators=[MinValueValidator(0)])
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.name

class Shipper(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateField(null=True)
    order_shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True)


class Option(models.Model):
    unit = models.CharField(max_length=255, blank=False, null=False)
    unit_in_stock = models.BigIntegerField(default=1, null=False, blank=False)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.unit

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
    product = models.OneToOneField(Option, on_delete=models.SET_NULL, null=True)
    product_voucher = models.OneToOneField('Voucher', on_delete=models.SET_NULL, null=True, blank=True)

class Bill(models.Model):
    value = models.DecimalField(max_digits=20, decimal_places=2,validators=[MinValueValidator(0)], null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    payed = models.BooleanField(default=False, null=False, blank=False)
    order_detail = models.OneToOneField(OrderDetail, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Rating(models.Model):
    rate = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Voucher(models.Model):
    discount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], null=False, blank=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    products = models.ManyToManyField(Product)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)