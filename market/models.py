import decimal

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.base_user import BaseUserManager 
# Create your models here.

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(null=False, blank=False, unique=True)
    phone_number = models.CharField(unique=True, blank=False, null=False, max_length=50)
    avatar = models.ImageField(upload_to='upload/%Y/%m', null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    balance = models.DecimalField(decimal_places=2, max_digits=20, validators=[MinValueValidator(decimal.Decimal('0.01'))])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    is_business = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name

class Address(models.Model):
    # Using GHN API Address for province_id, district_id, ward_id
    country = models.CharField(max_length=100, default="Viet Nam")
    province_id = models.IntegerField(blank=False, null=False)
    district_id = models.IntegerField(blank=False, null=False)
    ward_id = models.CharField(max_length=255, blank=False, null=False)
    street = models.CharField(max_length=255)
    full_address = models.TextField(default="ABC")
    note = models.TextField(null=True, blank=True)
    creator = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.full_address

class Category(models.Model):
    name = models.CharField(max_length= 255,unique=True, blank=False, null=False)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField(max_length= 255, blank=False, null=False)
    is_available = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category)
    sold_amount = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    picture = models.ImageField(upload_to='night_owl/product', null=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    @property
    def min_price(self):
        return Option.objects.filter(base_product=self).aggregate(models.Min('price')).get('price__min')

class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    can_destroy = models.BooleanField(default=True)
    completed_date = models.DateField(null=True)
    shipping_code = models.CharField(max_length=255, blank=True, null=True)
    total_shipping_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    note = models.TextField(null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customer_order')
    store = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='store_order')
    voucher_apply = models.ForeignKey('Voucher', on_delete=models.SET_NULL, null=True)

    STATUS_CHOICES = (
        (0, 'UnCheckout'),
        (1, 'Approving'),
        (2, 'Pending'),
        (3, 'Completed'),
        (4, 'Canceled'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    SHIPPING_CHOICES = (
        (0, 'COD'),
        (1, 'OnlinePaymentWithMomo'),
        (2, 'PaymentWithNightOwlAmount')
    )
    payment_type = models.IntegerField(choices=SHIPPING_CHOICES, default=0)


class Option(models.Model):
    unit = models.CharField(max_length=255, blank=False, null=False)
    unit_in_stock = models.PositiveBigIntegerField(default=1, null=False, blank=False)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    weight = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    height = models.PositiveIntegerField(default=1)
    width = models.PositiveIntegerField(default=1)
    length = models.PositiveIntegerField(default=1)

    base_product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.base_product.name + " " + self.unit

class Picture(models.Model):
    image = models.ImageField(upload_to='night_owl/product')
    product_option = models.ForeignKey(Option, on_delete=models.CASCADE)

class OrderDetail(models.Model):
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(1)], default=1)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    product_option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True)
    cart_id = models.ForeignKey('CartDetail', on_delete=models.SET_NULL, null=True)

class Bill(models.Model):
    value = models.DecimalField(max_digits=20, decimal_places=2,validators=[MinValueValidator(0)], null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    payed = models.BooleanField(default=False, null=False, blank=False)
    order_payed = models.OneToOneField(Order, on_delete=models.CASCADE, default=False)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class CartDetail(models.Model):
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product_option = models.ForeignKey(Option, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['customer', 'product_option']]

class Rating(models.Model):
    rate = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Voucher(models.Model):
    discount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], null=False, blank=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    code = models.TextField(default='nightowl', unique=True)
    is_percentage = models.BooleanField(default=False)
    products = models.ManyToManyField(Product)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class Room(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user = models.ManyToManyField(User)

    ROOMCHAT_CHOICES = (
        (0, 'single'),
        (1, 'group')
    )

    type = models.IntegerField(choices=ROOMCHAT_CHOICES, default=0)

class Message(models.Model):
    content = models.TextField(null=False, blank=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
