
from django.utils import timezone
from market.models import *
from django.db.models import Sum, F
from django.db import transaction


def check_now_in_datetime_range(start_date, end_date):
    now = timezone.now()
    return now >= start_date and now < end_date

def check_voucher_available(option_id, voucher_id):
    voucher = Voucher.objects.get(pk=voucher_id)
    option = Option.objects.get(pk=option_id)
    if option and voucher:
        if option.base_product.id in voucher.products.values_list('id', flat=True):
            return check_now_in_datetime_range(voucher.start_date, voucher.end_date)
    return False

def check_discount_in_order(order_details, voucher_id):
    for odd in order_details:
        if check_voucher_available(odd.product_option.id, voucher_id):
            return odd.id
    return None

def calculate_orderdetail_value_with_voucher(orderdetail, voucher):
    if voucher.is_percentage:
        return orderdetail.quantity * orderdetail.unit_price * (100-voucher.discount)
    return orderdetail.quantity * orderdetail.unit_price - voucher.discount


def calculate_value(order_id, voucher_code=None):
    order = Order.objects.get(pk=order_id)
    value = 0
    if order:
        order_details = order.orderdetail_set
        if voucher_code:
            voucher = Voucher.objects.first(code = voucher_code)
            if voucher:
                odd_exclude = check_discount_in_order(order_details.all(), voucher.id)
                if odd_exclude and check_voucher_available(odd_exclude.id, voucher.id):
                    order_details = order_details.exclude(pk=odd_exclude)
                    odd_exclude = OrderDetail.objects.get(pk=odd_exclude)
                    value = value + calculate_orderdetail_value_with_voucher(odd_exclude, voucher)
        value = value + order_details.aggregate(total_price = Sum(F('quantity') * F('unit_price')))['total_price']
    return value

def decrease_option_unit_instock(orderdetail_id):
    odd = OrderDetail.objects.get(pk=orderdetail_id)
    odd.product_option.unit_in_stock = F('odd.product_option.unit_in_stock') - odd.quantity
    if odd.product_option.unit_in_stock < 0:
        return False
    odd.product_option.save()
    return True

def checkout_order(order_id, voucher_id=None):
    # with transaction.atomic():
    #     order = (Order.objects.select_related('orderdetail__product_option', 'bill'))
    pass