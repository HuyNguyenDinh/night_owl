from dataclasses import field

from rest_framework.serializers import ModelSerializer, ReadOnlyField, ListField, IntegerField, SerializerMethodField, CharField, DictField, Serializer

from .models import *
import cloudinary
import cloudinary.uploader
from django.db.models import Sum, F
import decimal
from drf_extra_fields.fields import Base64ImageField


class AddressSerializer(ModelSerializer):

    class Meta:
        model = Address
        exclude = ["creator"]

class UserSerializer(ModelSerializer):
    address = AddressSerializer(required=False, read_only=True)
    cart_quantity = SerializerMethodField(method_name="count_cart_quantity", read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_business', 'password', 'is_active', 'verified', 'provider', 'avatar', 'address', 'cart_quantity', 'balance']
        extra_kwargs = {
            'password': {'write_only': 'true'},
            'is_staff': {'read_only': 'true'},
            'is_business': {'read_only': 'true'},
            'verified': {'read_only': 'true'},
            'is_active': {'read_only': 'true'},
            'balance': {'read_only': 'true'}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def count_cart_quantity(self, obj):
        return obj.cartdetail_set.all().count()

    
class UserLessInformationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'avatar']

class UserCashinSerializer(ModelSerializer):
    amount = IntegerField(write_only=True, required=True, min_value=10000)
    pay_url = CharField(read_only=True)
    class Meta:
        model = User
        fields = ['amount', 'pay_url']

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class OptionPictureSerializer(ModelSerializer):
    class Meta:
        model = Picture
        fields = "__all__"
        extra_kwargs = {
            'product_option': {'read_only': 'true'},
            'pk': {'read_only': 'true'}
        }

# Create multiple options
class CreateOptionSerializer(ModelSerializer):
    picture_set = OptionPictureSerializer(many=True, read_only=True)
    uploaded_images = ListField(
        child = Base64ImageField(allow_empty_file=False, required=True),
        write_only = True,
        required=True
    )
    class Meta:
        model = Option
        fields = ["id", "unit", "unit_in_stock", "price", "weight", "height", "width", "length", "base_product", "picture_set", "uploaded_images"]
        extra_kwargs = {
            'base_product': {'read_only': 'true'},
        }
    
    def create(self, validated_data):
        uploaded_data = validated_data.pop('uploaded_images')
        option = Option.objects.create(**validated_data)
        for uploaded_item in uploaded_data:
            new_product_image = Picture.objects.create(product_option = option, image = uploaded_item)
        return option

class OptionSerializer(ModelSerializer):
    picture_set = OptionPictureSerializer(many=True, required=False)
    class Meta:
        model = Option
        fields = "__all__"
        extra_kwargs = {
            'base_product': {'read_only': 'true'}
        }

# List product serializer
class ListProductSerializer(ModelSerializer):
    min_price = ReadOnlyField()
    categories = CategorySerializer(many=True)
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            'owner': {'read_only': 'true'},
            'sold_amount': {'read_only': 'true'},
        }

# Create product serializer
class ProductSerializer(ModelSerializer):
    min_price = ReadOnlyField()
    image = Base64ImageField(required=True, write_only=True)
    class Meta:
        model = Product
        fields = ["id", "name", "is_available", "sold_amount", "picture", "description", "owner", "image", "min_price", "categories"]
        extra_kwargs = {
            'owner': {'read_only': 'true'},
            'sold_amount': {'read_only': 'true'},
            'picture': {'read_only': 'true'},
            'image': {'write_only': 'true', 'required': 'true'}
        }
    
    def create(self, validated_data):
        category_set = validated_data.pop('categories')
        pd_img = validated_data.pop('image')
        pd = Product.objects.create(owner=self.context['request'].user, **validated_data, picture=pd_img)
        pd.categories.set(category_set)
        return pd

# show rating
class RatingSerializer(ModelSerializer):
    creator = UserSerializer()
    product = ProductSerializer()

    class Meta:
        model = Rating
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': 'true'},
        }

# Create rating
class CreateRatingSerializer(ModelSerializer):

    class Meta:
        model = Rating
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': 'true'},
            'creator': {'read_only': 'true'},
            'product': {'read_only': 'true'},
        }

# Get product detail
class ProductRetrieveSerializer(ModelSerializer):
    option_set = OptionSerializer(many=True)
    owner = UserSerializer()
    categories = CategorySerializer(many=True)
    rating_set = RatingSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"

# Get product id, name and picture
class ProductLessInformationSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'picture']

class OptionInOrderDetailSerializer(ModelSerializer):
    base_product = ProductLessInformationSerializer()
    class Meta:
        model = Option
        fields = ['id', 'unit', 'base_product', 'price']
        extra_kwargs = {
            'base_product': {'read_only': 'true'}
        }

class OrderDetailSerializer(ModelSerializer):
    product_option = OptionInOrderDetailSerializer(read_only=True)
    class Meta:
        model = OrderDetail
        fields = "__all__"

class ListOrderSerializer(ModelSerializer):
    store = UserLessInformationSerializer(read_only=True)
    customer = UserLessInformationSerializer(read_only=True)
    cost = SerializerMethodField(method_name='calculate_temp_price', read_only=True)
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {
            'status': {'read_only':'true'},
            'can_destroy': {'read_only': 'true'}
        }

    def calculate_temp_price(self, obj):
        try:
            bill = obj.bill
            return bill.value
        except:
            order_details = OrderDetail.objects.filter(order=obj)
            return order_details.aggregate(total_price=Sum(F('quantity') * F('unit_price')))['total_price']

class OrderSerializer(ModelSerializer):
    list_cart = ListField(
        child = IntegerField(),
        write_only=True
    )
    orderdetail_set = OrderDetailSerializer(many=True, read_only=True)
    cost = SerializerMethodField(method_name='calculate_temp_price', read_only=True)
    store = UserLessInformationSerializer(read_only=True)
    customer = UserLessInformationSerializer(read_only=True)
    class Meta:
        model = Order
        fields = "__all__"
        extra_kwargs = {
            'status': {'read_only':'true'},
            'can_destroy': {'read_only': 'true'},
            'store' : {'read_only': 'true'},
            'customer': {'read_only': 'true'},
            'payment_type': {'read_only': 'true'}
        }
    
    def create(self, validated_data):
        _ = validated_data.pop('list_cart')
        return super().create(validated_data)

    def calculate_temp_price(self, obj):
        try:
            bill = obj.bill
            return bill.value
        except:
            order_details = OrderDetail.objects.filter(order=obj)
            return order_details.aggregate(total_price=Sum(F('quantity') * F('unit_price')))['total_price']

class VoucherSerializer(ModelSerializer):

    class Meta:
        model = Voucher
        fields = "__all__"
        extra_kwargs = {
            'creator': {'read_only': 'true'}
        }


class CheckoutOrderSerializer(ModelSerializer):
    list_voucher = DictField(
        child = CharField(),
        write_only=True,
        required=False
    )
    payment_type = IntegerField(max_value=2, min_value=0, required=False)
    class Meta:
        model = Order
        exclude = ['customer']
        extra_kwargs = {
            'order_date' : {'read_only': 'true'},
            'completed_date' : {'read_only': 'true'},
            'shipping_code' : {'read_only': 'true'},
            'total_shipping_fee' : {'read_only': 'true'},
            'note' : {'read_only': 'true'},
            'status': {'read_only':'true'},
            'can_destroy': {'read_only': 'true'},
            'store' : {'read_only': 'true'},
            'voucher_apply': {'read_only': 'true'},
            'payment_type': {'read_only': 'true'}
        }


class BillSerializer(ModelSerializer):

    class Meta:
        model = Bill
        fields = "__all__"

# Show product option in cart detail
class OptionInCartSerializer(ModelSerializer):
    base_product = ProductSerializer(read_only=True)
    class Meta:
        model = Option
        fields = "__all__"
        depth = 2

# Get User's cart detail
class CartSerializer(ModelSerializer):
    product_option = OptionInCartSerializer(read_only=True)

    class Meta:
        model = CartDetail
        fields = "__all__"
        extra_kwargs = {
            'customer': {'read_only': True},
        }

class CartInStoreSerializer(ModelSerializer):
    carts = SerializerMethodField('get_carts_user', read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'avatar', 'address', 'carts']
        extra_kwargs = {
            'id': {'read_only': 'true'},
            'first_name': {'read_only': 'true'},
            'last_name': {'read_only': 'true'},
            'avatar': {'read_only': 'true'},
        }
    
    def get_carts_user(self, obj):
        carts = CartDetail.objects.filter(product_option__base_product__owner=obj, customer=self.context.get('request').user)
        serializer = CartSerializer(carts, many=True)
        return serializer.data


# Add to cart
class AddCartSerializer(ModelSerializer):
    
    class Meta:
        model = CartDetail
        fields = "__all__"
        extra_kwargs = {
            'customer': {'read_only': 'true'},
            'product_option': {'read_only': 'true'},
        }

class GoogleTokenSerializer(Serializer):
    id_token = CharField(required=True, write_only=True)
    email = CharField(read_only=True)
    first_name = CharField(read_only=True)
    last_name = CharField(read_only=True)