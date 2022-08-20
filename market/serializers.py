from rest_framework.serializers import  ModelSerializer
from .models import *
import cloudinary
import cloudinary.uploader



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "username", "password", "avatar", "phone_number"]
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

class CreateProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        exclude = ("sold_amount", "owner")

class ProductSerializer(ModelSerializer):
    
    class Meta:
        model = Product
        fields = "__all__"

class ProductRetrieveSerializer(ModelSerializer):
    option_set = OptionsSerializer(many=True)
    owner = UserSerializer()
    categories = CategorySerializer(many=True)

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

class RatingSerializer(ModelSerializer):
    creator = UserSerializer()

    class Meta:
        model = Rating
        fields = "__all__"

class CartSerializer(ModelSerializer):
    
    class Meta:
        model = CartDetail
        fields = "__all__"

class VoucherSerializer(ModelSerializer):

    class Meta:
        model = Voucher
        fields = "__all__"