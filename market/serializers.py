from xml.etree.ElementTree import Comment
from rest_framework.serializers import  ModelSerializer, ReadOnlyField, ImageField, ListField
from .models import *
import cloudinary
import cloudinary.uploader
from drf_writable_nested.serializers import WritableNestedModelSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_business', 'password', 'is_active', 'verified', 'provider', 'avatar']
        extra_kwargs = {
            'password': {'write_only': 'true'},
        }
    
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

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
    

class CreateOptionSerializer(ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"
        extra_kwargs = {
            'base_product': {'read_only': 'true'},
            'picture_set': {'read_only': 'true'}
        }

class OptionSerializer(ModelSerializer):
    picture_set = OptionPictureSerializer(many=True, required=False)
    class Meta:
        model = Option
        fields = "__all__"
        extra_kwargs = {
            'base_product': {'read_only': 'true'}
        }

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
        pd = Product(owner=self.context['request'].user)
        pd.name = validated_data['name']
        if validated_data.get('is_available'):
            pd.is_available = validated_data['is_available']
        if validated_data.get('picture'):
            pd.picture = validated_data['picture']
        if validated_data.get('description'):
            pd.description = validated_data['description']
        pd.save()
        pd.categories.set(validated_data['categories'])
        return pd

class RatingSerializer(ModelSerializer):
    creator = UserSerializer()
    product = ProductSerializer()

    class Meta:
        model = Rating
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': 'true'},
        }

class CreateRatingSerializer(ModelSerializer):

    class Meta:
        model = Rating
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': 'true'},
            'creator': {'read_only': 'true'},
            'product': {'read_only': 'true'},
        }

class ProductRetrieveSerializer(ModelSerializer):
    option_set = OptionSerializer(many=True)
    owner = UserSerializer()
    categories = CategorySerializer(many=True)
    rating_set = RatingSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"

class OrderDetailSerializer(ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = "__all__"

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class AddressSerializer(ModelSerializer):

    class Meta:
        model = Address
        fields = "__all__"

class BillSerializer(ModelSerializer):

    class Meta:
        model = Bill
        fields = "__all__"


class CartSerializer(ModelSerializer):
    
    class Meta:
        model = CartDetail
        fields = "__all__"

class VoucherSerializer(ModelSerializer):

    class Meta:
        model = Voucher
        fields = "__all__"