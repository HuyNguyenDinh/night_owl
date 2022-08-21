from xml.etree.ElementTree import Comment
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.decorators import action
from rest_framework import status, generics, viewsets, permissions
from .models import *
from .serializers import *
from .perms import *
from .paginators import *
from django.db.models import Q
# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    parser_classes = [MultiPartParser, FileUploadParser]
    serializer_class = UserSerializer

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []

        return super().get_parsers()

    @action(methods=['get'], detail=False, url_path='current-user')
    def get_current_user(self, request):
        current_user = User.objects.get(pk=request.user.id)
        if current_user:
            return Response(UserSerializer(current_user).data, status=status.HTTP_200_OK)
        return Response({'message': "Current user not found"}, status = status.HTTP_404_NOT_FOUND)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny(), ]
        return [permissions.IsAuthenticated(), ]

class CartDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return CartDetail.objects.filter(customer = self.request.user.id)

class ProductViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FileUploadParser]
    pagination_class = BasePagination
    permission_classes = [permissions.AllowAny]

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []

        return super().get_parsers()

    #
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny(), ]
        return [BusinessPermission(), ]
    #

    def get_queryset(self):
        products = Product.objects.all()
        if self.action in ["update", "destroy"]:
            products = products.filter(owner=self.request.user.id)
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

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        pd = Product.objects.get(pk=pk)
        comments = Rating.objects.filter(product = pd)
        if comments:
            return Response(RatingSerializer(comments, many=True).data, status=status.HTTP_200_OK)
        return Response({'message': 'This product had no comment'}, status = status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True, url_path='options')
    def get_options(self, request, pk):
        options = Product.objects.get(pk=pk).option_set.all()
        options = options.filter(unit_in_stock__gt=0)
        return Response(OptionsSerializer(options, many=True).data, status=status.HTTP_200_OK)
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
    permission_classes = [permissions.AllowAny]

    # def get_permissions(self):
    #     if self.action in ["list", "retrieve"]:
    #         return [permissions.AllowAny(), ]
    #     return [NightOwlPermission(), ]

class OptionViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionsSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny(), ]
        return [NightOwlPermission(), ]

class OrderViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveDestroyAPIView):
    serializer_class = OrderSerializer
    pagination_class = BasePagination
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        orders = Order.objects.filter(Q(customer = self.request.user.id) | Q(store = self.request.user.id))
        return orders

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    pagination_class = ProductPagination
    permission_classes = [permissions.IsAuthenticated]
