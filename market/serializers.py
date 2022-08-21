from xml.etree.ElementTree import Comment
from rest_framework.serializers import  ModelSerializer
from .models import *
import cloudinary
import cloudinary.uploader



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
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

class OptionsPictureSerializer(ModelSerializer):

    class Meta:
        model = Picture
        fields = "__all__"
        extra_kwargs = {
            'image': {'write_only': 'true'},
            'link': {'read_only': 'true'},
        }
    

class OptionsSerializer(ModelSerializer):
    picture_set = OptionsPictureSerializer(many=True)
    class Meta:
        model = Option
        fields = '__all__'


class ProductSerializer(ModelSerializer):

    categories = CategorySerializer(many=True)
    
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            'owner': {'read_only': 'true'},
            'sold_amount': {'read_only': 'true'}
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

    class Meta:
        model = Rating
        fields = "__all__"

class ProductRetrieveSerializer(ModelSerializer):
    option_set = OptionsSerializer(many=True)
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