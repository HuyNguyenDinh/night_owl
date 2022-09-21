from django.utils import timezone
from market.models import *
from django.db.models import Sum, F, Max
from django.db import transaction
import requests
import json
from market.serializers import *
import decimal

############ Order #############
# Checkout Order: Decrease unit in stock of option in order details ->
# Calculate value order (Get order detail that match the voucher id -> check voucher) to create bill ->
# 

# Check voucher available at now
def check_now_in_datetime_range(start_date, end_date):
    now = timezone.now()
    return now >= start_date and now <= end_date

# Check voucher
def check_voucher_available(option_id, voucher_id):
    voucher = Voucher.objects.get(pk=voucher_id)
    option = Option.objects.get(pk=option_id)
    if option and voucher:
        if option.base_product.id in voucher.products.values_list('id', flat=True):
            return check_now_in_datetime_range(voucher.start_date, voucher.end_date)
    return False

# Get order detail id match the voucher
def check_discount_in_order(order_details, voucher_id):
    for odd in order_details:
        if check_voucher_available(odd.product_option.id, voucher_id):
            return odd.id
    return None

def calculate_order_value_with_voucher(voucher, value):
    if voucher.is_percentage:
        return value * (100-voucher.discount)
    return value - voucher.discount

def calculate_value(order_id, voucher_id=None):
    order = Order.objects.get(pk=order_id)
    print(order.id)
    value = 0
    if order:
        value = order.orderdetail_set.aggregate(total_price = Sum(F('quantity') * F('unit_price')))['total_price']
        print(type(value))
        if voucher_id:
            voucher = Voucher.objects.get(pk=voucher_id)
            if voucher:
                odd_exclude = check_discount_in_order(order.orderdetail_set.all(), voucher.id)
                if odd_exclude and check_voucher_available(odd_exclude.id, voucher.id):
                    value = calculate_order_value_with_voucher(voucher, value)
    return value

# decrease the unit in stock of option when checkout the order
@transaction.atomic
def decrease_option_unit_instock(orderdetail_id):
    odd = OrderDetail.objects.get(pk=orderdetail_id)
    print(odd.id)
    option = Option.objects.select_for_update().get(orderdetail__id=orderdetail_id)
    print(option.id)
    option.unit_in_stock = option.unit_in_stock - odd.quantity
    print(option.unit_in_stock)
    option.save()
    option.refresh_from_db()
    return option

# Calculate Max Width, Height, Length
def calculate_max_lwh(order_id):
    order = Order.objects.get(pk=order_id)
    max_lwh = order.orderdetail_set.all().aggregate(
        max_width = Max('product_option__width'),
        max_height=Max('product_option__height'), 
        max_length=Max('product_option__length'),
        total_weight = Sum(F('product_option__weight')))
    return max_lwh

# POST request to create shipping order
def create_shipping_order(order_id):
    order = Order.objects.get(pk=order_id)
    seller = order.store
    customer = order.customer
    max_lwh = calculate_max_lwh(order_id=order.id)
    value = order.bill.value
    items = []
    for i in order.orderdetail_set.all():
        item = {
            "name": i.product_option.base_product.name,
            "code": str(i.product_option.id),
            "quantity": i.quantity,
            "price": int(i.unit_price),
            "length": i.product_option.length,
            "width": i.product_option.length,
            "height": i.product_option.height
        }
        items.append(item)
    data = {
            "payment_type_id": 2,
            "note": "Night Owl Market",
            "required_note": "KHONGCHOXEMHANG",
            "return_phone": seller.phone_number,
            "return_address": seller.address.full_address,
            "return_district_id": None,
            "return_ward_code": seller.address.ward_id,
            "client_order_code": str(order.id),
            "to_name": customer.last_name + " " + customer.first_name,
            "to_phone": customer.phone_number,
            "to_address": customer.address.full_address,
            "to_ward_code": customer.address.ward_id,
            "to_district_id": customer.address.district_id,
            "cod_amount": int(value),
            "content": order.note,
            "weight": max_lwh.get('total_weight'),
            "length": max_lwh.get('max_length'),
            "width": max_lwh.get('max_width'),
            "height": max_lwh.get('max_height'),
            "deliver_station_id": None,
            "insurance_value": int(value),
            "service_type_id":2,
            "coupon": None,
            "items": items
        }
    r = json.dumps(data)
    loaded_r = json.loads(r)
    header = {
        'Content-Type': 'application/json',
        'ShopId': '117552',
        'Token': '8ae8d191-18b9-11ed-b136-06951b6b7f89'
    }
    url = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create'

    x = requests.post(url=url, json=loaded_r, headers=header)
    return x.text

@transaction.atomic
def checkout_order(order_id, voucher_code=None):
    order = Order.objects.select_for_update().get(pk=order_id)
    print(order.id)
    for i in order.orderdetail_set.all():
        print("Order detail", i.id)
        decrease_option_unit_instock(i.id)

    # update status
    order.status = 1
    order.save()
    print(order.id)
    # calculate value to create bill
    value = 0
    voucher = None
    if voucher_code and voucher_code.get(order.id):
        print('voucher id got')
        voucher = Voucher.objects.filter(code = voucher_code)
    if voucher:
        print('voucher got')
        value=calculate_value(order_id=order.id, voucher_id=voucher[0].id)
    else:
        print('no voucher')
        value=calculate_value(order_id=order.id)
    print('calculated value')
    _ = Bill.objects.create(value=value, order_payed=order, customer=order.customer)
    print('created bill')
    order.refresh_from_db()
    return order

# Calculate shipping fee
def calculate_shipping_fee(order_id):
    order = Order.objects.get(pk=order_id)
    store = order.store
    customer = order.customer
    max_lwh = calculate_max_lwh(order_id=order.id)
    data = {
        "from_district_id":store.address.district_id,
        "service_type_id":2,
        "to_district_id":customer.address.district_id,
        "to_ward_code":customer.address.ward_id,
        "height":max_lwh['max_height'],
        "length":max_lwh['max_length'],
        "weight":max_lwh['total_weight'],
        "width":max_lwh['max_width'],
        "insurance_value": int(calculate_value(order_id=order.id)),
        "coupon": None
    }
    r = json.dumps(data)
    loaded_r = json.loads(r)
    url = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee'
    headers = {
        'Content-Type': 'application/json',
        'ShopId': '117552',
        'Token': '8ae8d191-18b9-11ed-b136-06951b6b7f89'
    }
    x = requests.post(url=url, json=loaded_r, headers=headers)
    return x.text

# Create shipping code that match with order
@transaction.atomic
def update_shipping_code(order_id):
    order = Order.objects.select_for_update().get(pk=order_id)
    shipping_order = json.loads(create_shipping_order(order_id=order.id))
    if shipping_order.get('code') == 200:
        data = shipping_order.get('data')
        order.shipping_code = data.get('order_code')
        order.total_shipping_fee = data.get('total_fee')
        order.save()
        return True
    return False

@transaction.atomic
def make_order_from_list_cart(list_cart_id, user_id, data):
    carts = CartDetail.objects.filter(customer__id=user_id, id__in=list_cart_id)
    user = User.objects.get(pk=user_id)
    result = []
    if carts:
        stores = User.objects.filter(product__option__cartdetail__in=carts).distinct().exclude(id = user_id)
        for store in stores:
            cart_order = carts.filter(product_option__base_product__owner=store)
            if cart_order:
                serializer = OrderSerializer(data=data)
                if serializer.is_valid(raise_exception=True):   
                    order = serializer.save(store=store, customer=user)
                    order.save()
                    for c in cart_order:
                        _ = OrderDetail.objects.create(quantity=c.quantity, product_option= c.product_option, unit_price= c.product_option.price, order=order, cart_id=c)
                    shipping_data = json.loads(calculate_shipping_fee(order_id=order.id))
                    if shipping_data.get('code') == 200:
                        shipping_fee = shipping_data.get('data').get('total')
                        order.total_shipping_fee = shipping_fee
                        order.save()
                        order.refresh_from_db()
                    result.append(order)
    return result