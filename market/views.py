from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.decorators import action
from rest_framework import status, generics, views
from .models import *
from .serializers import *
# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    parser_classes = [MultiPartParser, FileUploadParser]
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    parser_classes = [MultiPartParser, FileUploadParser]

    def get_queryset(self):
        products = Product.objects.filter(is_available=True)

        search = self.request.query_params.get("search")

        if search is not None:
            products = products.filter(name__icontains=search)

        cate_id = self.request.query_params.get('category_id')
        if cate_id is not None:
            products = products.filter(categories_id=cate_id)
        
        return products

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductRetrieveSerializer
        return ProductSerializer
    @action(methods=['get'], detail=True, url_path='options')
    def get_options(self, request, pk):
        options = Product.objects.get(pk=pk).option_set.all()
        options = options.filter(unit_in_stock__gt=0)
        return Response(OptionsSerializer(options, many=True).data, status=status.HTTP_200_OK)
    
class CategoryViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class OptionViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionsSerializer