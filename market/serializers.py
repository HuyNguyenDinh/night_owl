from copyreg import pickle
from rest_framework.serializers import  ModelSerializer, ImageField
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
    image = ImageField()

    class Meta:
        model = Picture
        fields = "__all__"
        extra_kwargs = {
            'image': {'write_only': 'true'},
            'link': {'read_only': 'true'},
        }
    
    def create(self, validated_data):
        res = cloudinary.uploader.upload(validated_data['image'])
        res = pickle.dump(res)
    

class OptionsSerializer(ModelSerializer):
    picture_set = OptionsPictureSerializer(many=True)
    class Meta:
        model = Option
        fields = '__all__' 

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"