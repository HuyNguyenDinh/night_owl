from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(Bill)
admin.site.register(Option)
admin.site.register(Picture)
admin.site.register(Rating)