from django.db import router
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .admin import *
from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet)
router.register("products", views.ProductViewSet)
router.register("category", views.CategoryViewSet)
router.register("options", views.OptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]