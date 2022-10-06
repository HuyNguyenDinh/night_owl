from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import *
from django import forms

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    pk_name = 'product_option'

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = "__all__"
class UserAdmin(admin.ModelAdmin):
    search_fields = ['id', 'email', 'phone_number']

class PictureInLine(admin.TabularInline):
    model = Picture
    pk_name = 'product_option'

class OptionInLine(admin.TabularInline):
    model = Option
    pk_name = 'base_product'

class OptionAdmin(admin.ModelAdmin):
    form = OptionForm
    search_fields = ['id', 'base_product__id', 'base_product__name', 'base_product__owner__id',\
                     'base_product__owner__email', 'base_product__owner__phone_number']
    inlines = (PictureInLine, OrderDetailInline)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name', 'owner__id', 'owner__email', 'owner__phone_number']
    inlines = (OptionInLine, )
    form = ProductForm

class AddressInline(admin.TabularInline):
    model = Address
    pk_name = 'creator'

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

class UserAdmin(admin.ModelAdmin):
    inlines = (AddressInline, )
    form = UserForm
    search_fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = "__all__"

class  ReplyInline(admin.TabularInline):
    model = Reply
    pk_name = 'report'

class ReportAdmin(admin.ModelAdmin):
    form = ReportForm
    search_fields = ['id', 'reporter__email', 'reporter__phone_number']
    list_filter = ['status', 'created_date']
    inlines = [ReplyInline, ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.creator = request.user
            instance.save()
        formset.save_m2m()

class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderDetail
        fields = "__all__"
class OrderDetailAdmin(admin.ModelAdmin):
    form = OrderDetailForm
    search_fields = ['id', 'order__id', 'order__store__id', 'order__store__email', 'order__store__phone_numer',\
                     'order__customer__id', 'order__customer__email', 'order__customer__phone_numer']

class BillInline(admin.TabularInline):
    model = Bill
    pk_name = 'order_payed'

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDetailInline, BillInline]
    form = OrderForm
    search_fields = ['id', 'store__id', 'store__email', 'store__phone_numer', 'customer__id', 'customer__email',\
                     'customer__phone_numer']

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(Bill)
admin.site.register(Option, OptionAdmin)
admin.site.register(Picture)
admin.site.register(Rating)
admin.site.register(CartDetail)
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Report, ReportAdmin)
