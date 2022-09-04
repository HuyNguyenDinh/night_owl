from rest_framework.pagination import PageNumberPagination

class CategoryPagination(PageNumberPagination):
    page_size = 8

class BasePagination(PageNumberPagination):
    page_size = 20

class ProductPagination(PageNumberPagination):
    page_size = 16

class CommentPagination(PageNumberPagination):
    page_size = 10

class OrderPagination(PageNumberPagination):
    page_size = 5