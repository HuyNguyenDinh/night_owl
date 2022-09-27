from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .admin import *
from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet)
router.register("products", views.ProductViewSet, basename="products")
router.register("category", views.CategoryViewSet, basename="category")
router.register("options", views.OptionViewSet, basename="options")
router.register("orders", views.OrderViewSet, basename="orders")
router.register("order-detail", views.OrderDetailViewSet, basename="order-detail")
router.register("bills", views.BillViewSet, basename="bills")
router.register("cart", views.CartDetailViewSet, basename="cart")
router.register("address", views.AddressViewSet, basename="user_address")
router.register("voucher", views.VoucherViewSet, basename="voucher")


urlpatterns = [
    path('', include(router.urls)),
    path('momo-payed/<str:secret_link>/', views.MomoPayedView.as_view())
]