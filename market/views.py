from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.decorators import action
from rest_framework import status, generics, views
from .models import *
from .serializers import *
from .perms import *
from .paginators import *
# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    parser_classes = [MultiPartParser, FileUploadParser]
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FileUploadParser]
    pagination_class = ProductPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny(), ]
        return [BusinessPermission(), ]

    def get_queryset(self):
        products = Product.objects.all()
        if self.action in ["update", "destroy"]:
            products = products.filter(owner=self.request.user)
        elif self.action in ["list", "retrieve"]:
            products = products.filter(is_available=True)

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
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny(), ]
        return [NightOwlPermission(), ]

class OptionViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionsSerializer

class OrderViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveDestroyAPIView):
    serializer_class = OrderSerializer
    pagination_class = BasePagination
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        orders = Order.objects.all()
        if self.action in ["retrieve", "destroy"]:
            orders = orders.filter(customer = self.request.user)
        return orders

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    pagination_class = ProductPagination