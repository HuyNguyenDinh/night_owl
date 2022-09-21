from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.decorators import action
from rest_framework import status, generics, viewsets, permissions
from .models import *
from .serializers import *
from .perms import *
from .paginations import *
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from market.utils import *
# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    parser_classes = [MultiPartParser, JSONParser]
    serializer_class = UserSerializer
    pagination_class = None

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

class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCreator]
    serializer_class = AddressSerializer

    def get_permissions(self):
        if action == 'create':
            return [permissions.IsAuthenticated(), ]
        return [IsCreator(), ]
    def get_queryset(self):
        return Address.objects.filter(creator__id = self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(creator=request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({'message': 'cannot add address to your account'}, status=status.HTTP_400_BAD_REQUEST)

class CartDetailViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    pagination_class = None

    def get_queryset(self):
        return CartDetail.objects.filter(customer = self.request.user.id)

    @action(methods=['get'], detail=False, url_path='get-cart-groupby-owner')
    def get_cart_groupby_owner(self, request):
        cart = CartDetail.objects.filter(customer__id=request.user.id).all().values_list('id')
        owner = User.objects.filter(product__option__cartdetail__id__in=cart).distinct()
        carts = CartInStoreSerializer(owner, context={'request': request}, many=True)
        if carts:
            return Response(carts.data, status=status.HTTP_200_OK)
        return Response({'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, JSONParser]
    pagination_class = BasePagination
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['sold_amount', 'owner']
    search_fields = ['name', 'owner__first_name', 'owner__last_name']
    ordering_fields = ['sold_amount']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []

        return super().get_parsers()

    # def get_serializer_class(self):
    #     if action == 'add_option':
    #         return CreateOptionSerializer
    #     return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["list", "retrieve", "get_comments", "get_options"]:
            return [permissions.AllowAny(), ]
        elif self.action == 'add_comment':
            return [permissions.IsAuthenticated(), ]
        elif self.action == 'create':
            return [BusinessPermission(), ]
        return [BusinessOwnerPermission(), ]

    def get_queryset(self):
        products = Product.objects.all()
        if self.action in ["update", "destroy", "add_option"]:
            products = products.filter(owner=self.request.user.id)
        elif self.action in ["list", "retrieve"]:
            products = products.filter(option__isnull=False).distinct()

        cate_id = self.request.query_params.get('category_id')
        if cate_id is not None:
            products = products.filter(categories=cate_id)
        return products

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductRetrieveSerializer
        elif self.action == 'add_comment':
            return CreateRatingSerializer
        elif self.action == 'add_option':
            return CreateOptionSerializer
        elif self.action == 'list':
            return ListProductSerializer
        return ProductSerializer

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        pd = Product.objects.get(pk=pk)
        comments = Rating.objects.filter(product = pd)
        if comments:
            return Response(RatingSerializer(comments, many=True).data, status=status.HTTP_200_OK)
        return Response({'message': 'This product had no comment'}, status = status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True, url_path='add-comment')
    def add_comment(self, request, pk):
        pd = Product.objects.get(pk=pk)
        try:
            self.check_object_permissions(request, pd)
            serializer = CreateRatingSerializer(data=request.data)
            print(request.data)
            if serializer.is_valid():
                serializer.save(creator=request.user, product=pd)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'message': 'not valid comment'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'please login to comment'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(methods=['post'], detail=True, url_path='add-option')
    def add_option(self, request, pk):
        pd = Product.objects.get(pk=pk)
        try:
            self.check_object_permissions(request, pd)
            serializer = CreateOptionSerializer(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(base_product=pd)
                if request.data.getlist('image_set'):
                    for img in request.data.getlist('image_set'):
                        try:
                            _ = Picture.objects.create(image=img, product_option=obj)
                        except:
                            return Response({'message': "added option to product but cannot add picture to options"},
                                            status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response({'message': "cannot add options to product"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'you do not have permission'}, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['get'], detail=True, url_path='options')
    def get_options(self, request, pk):
        options = Product.objects.get(pk=pk).option_set.all()
        options = options.filter(unit_in_stock__gt=0)
        if options:
            return Response(OptionSerializer(options, many=True).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny(), ]
        return [permissions.IsAdminUser(), ]

class OptionViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny(), ]
        elif self.action == 'add_to_cart':
            return [permissions.IsAuthenticated(), ]
        return [BusinessPermission(), IsProductOptionOwner(), ]

    def get_serializer_class(self):
        if self.action == 'add_to_cart':
            return CartSerializer
        return OptionSerializer
    
    @action(methods=['post'], detail=True, url_path='add-to-cart')
    def add_to_cart(self, request, pk):
        op = Option.objects.get(pk=pk)
        cart = CartSerializer(data=request.data)
        if cart.is_valid():
            cart.save(customer=request.user, product_option=op)
            return Response(cart.data, status=status.HTTP_201_CREATED)
        return Response({'message': 'cannot add product to your cart'}, status=status.HTTP_400_BAD_REQUEST)
        

class OrderViewSet(viewsets.ModelViewSet):
    pagination_class = OrderPagination
    permission_classes = [permissions.IsAuthenticated,]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'id', 'can_destroy', 'completed_date', 'order_date']
    ordering_fields = ['completed_date', 'order_date', 'bill__value']

    def get_serializer_class(self):
        if self.action in ["list"]:
            return ListOrderSerializer
        elif self.action == 'checkout':
            return CheckoutOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        orders = Order.objects.filter(Q(customer = self.request.user.id) | Q(store = self.request.user.id))
        state = self.request.query_params.get('state')
        if state:
            if state == '0':
                orders =  orders.filter(customer = self.request.user.id)
            elif state == '1':
                orders =  orders.filter(store = self.request.user.id)
        return orders 

    def create(self, request, *args, **kwargs):
        list_cart = request.data.get('list_cart')
        if list_cart:
            result = make_order_from_list_cart(list_cart_id=list_cart, user_id=request.user.id, data=request.data)
            if result:
                return Response(OrderSerializer(result, many=True).data, status=status.HTTP_201_CREATED)
            return Response({'message': 'wrong cart id, not found cart'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'you must add array of your cart id'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(methods=['get'], detail=False, url_path='cancel_uncheckout_order')
    def cancel_uncheckout_order(self, request):
        order = Order.objects.filter(customer = request.user.id, status=0)
        if order:
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'not found uncheckout order'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=False, url_path='checkout_order')
    def checkout(self, request):
        order = Order.objects.filter(customer = request.user.id, status=0)
        if order:
            odd_id_list = order.values_list('orderdetail__cart_id__id', flat=True)
            voucher_code = request.data.get('list_voucher')
            success = False
            try:
                for o in order:
                    result = checkout_order(order_id=o.id, voucher_code=voucher_code)
                    if result is None:
                        raise Exception
                success = True
            except:
                return Response({'message':'some product options has out of stock'}, status=status.HTTP_400_BAD_REQUEST)
            if success:
                cart = CartDetail.objects.filter(orderdetail__id__in=odd_id_list)
                if cart.count() > 0:
                    cart.delete()
                return Response(OrderSerializer(result).data, status=status.HTTP_202_ACCEPTED)
            return Response({'message': 'can not checkout the orders'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'message': 'can not found the orders uncheckout'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True, url_path='accept_order')
    def accept_order(self, request, pk):
        order = Order.objects.get(pk=pk, status=1)
        if order:
            pass

class OrderDetailViewSet(viewsets.ModelViewSet):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        status = self.request.query_params.get('status')
        ordd = OrderDetail.objects.filter(Q(order__customer__id=self.request.user.id) |
                                          Q(order__store__id=self.request.user.id))
        if status:
            ordd.filter(order__status=status)
        return ordd

class BillViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    pagination_class = ProductPagination
    permission_classes = [permissions.IsAuthenticated]

class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer
    pagination_class = BasePagination

    def create(self, request, *args, **kwargs):
        can_add = False
        # Check night owl staff
        if request.user and request.user.is_staff:
            can_add = True
        else:
            products = Product.objects.filter(owner=request.user.id,
                                   id__in=[o for o in request.data.get('products')])
            # Check product owner in list product
            if list(products.values_list('id', flat=True)) == request.data.get('products'):
                can_add = True
        if can_add:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(creator=request.user)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return Response({'message': 'can not create voucher'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'can not add voucher to product that you are not the owner'},
                        status=status.HTTP_403_FORBIDDEN)
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny(), ]
        elif self.action == 'create':
            return [BusinessPermission(), ]
        return [BusinessOwnerPermission(), ]
