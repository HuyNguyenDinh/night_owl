from dataclasses import field
from rest_framework.serializers import  ModelSerializer, ReadOnlyField, ListField, IntegerField, SerializerMethodField, ImageField, CharField, DictField, Serializer, DecimalField
from .models import *
import cloudinary
import cloudinary.uploader
from django.db.models import Sum, F
import decimal


class AddressSerializer(ModelSerializer):

    class Meta:
        model = Address
        exclude = ["creator"]

class UserSerializer(ModelSerializer):
    address = AddressSerializer(required=False, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_business', 'password', 'is_active', 'verified', 'provider', 'avatar', 'address']
        extra_kwargs = {
            'password': {'write_only': 'true'},
            'is_staff': {'read_only': 'true'},
            'is_business': {'read_only': 'true'},
            'verified': {'read_only': 'true'},
            'is_active': {'read_only': 'true'},
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
class UserLessInformationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'avatar']

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class OptionPictureSerializer(ModelSerializer):
    class Meta:
        model = Picture
        fields = "__all__"
        extra_kwargs = {
            'product_option': {'read_only': 'true'}
        }

# Create multiple options
class CreateOptionSerializer(ModelSerializer):
    image_set = ListField(
        child = ImageField(),
        write_only=True
    )
    picture_set = OptionPictureSerializer(many=True, read_only=True)
    class Meta:
        model = Option
        fields = "__all__"
        extra_kwargs = {
            'base_product': {'read_only': 'true'},
        }
    
    def create(self, validated_data):
        pictures = validated_data.pop('image_set')
        option = Option(**validated_data)
        option.save()
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

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            'owner': {'read_only': 'true'},
            'sold_amount': {'read_only': 'true'},
        }
    
    def create(self, validated_data):
        category_set = validated_data.pop('categories')
        pd = Product.objects.create(owner=self.context['request'].user, **validated_data)
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
            return order_details.aggregate(total_price = Sum(F('quantity') * F('unit_price')))['total_price']

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
            return order_details.aggregate(total_price = Sum(F('quantity') * F('unit_price')))['total_price']

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
            'customer': {'read_only': 'true'},
        }

    def to_representation(self, instance):
        return super().to_representation(instance)

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
