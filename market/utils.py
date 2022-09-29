from django.utils import timezone
from market.models import *
from django.db.models import Sum, F, Max
from django.db import transaction
import requests
import json
from market.serializers import *
from threading import Thread
from night_owl_market import settings
from django.core.mail import send_mail

############ Order #############
# Checkout Order: Decrease unit in stock of option in order details ->
# Calculate value order (Get order detail that match the voucher id -> check voucher) to create bill ->
# 

# Check voucher available at now
def check_now_in_datetime_range(start_date, end_date):
    now = timezone.now()
    if end_date is not None:
        return now >= start_date and now <= end_date
    else:
        return now >= start_date

# Check voucher
def check_voucher_available(option_id, voucher_id):
    voucher = Voucher.objects.get(pk=voucher_id)
    option = Option.objects.get(pk=option_id)
    if option and voucher:
        if option.base_product.id in list(set(voucher.products.values_list('id', flat=True))):
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
        return value * (100-voucher.discount) / 100
    return value - voucher.discount

def calculate_value(order_id, voucher_id=None):
    order = Order.objects.get(pk=order_id)
    value = 0
    if order:
        value = order.orderdetail_set.aggregate(total_price=Sum(F('quantity') * F('unit_price')))['total_price']
        if voucher_id:
            voucher = Voucher.objects.get(pk=voucher_id)
            if voucher:
                odd_exclude = check_discount_in_order(order.orderdetail_set.all(), voucher.id)
                if odd_exclude:
                    order_detail = OrderDetail.objects.get(pk=odd_exclude)
                    if order_detail:
                        value = calculate_order_value_with_voucher(voucher, value)
        value = value + order.total_shipping_fee
    return value

# decrease the unit in stock of option when checkout the order
@transaction.atomic
def decrease_option_unit_instock(orderdetail_id):
    odd = OrderDetail.objects.get(pk=orderdetail_id)
    option = Option.objects.select_for_update().get(orderdetail__id=orderdetail_id)
    option.unit_in_stock = F('unit_in_stock') - odd.quantity
    option.save()
    product = Product.objects.select_for_update().get(pk=option.base_product.id)
    product.sold_amount = F('sold_amount') + odd.quantity
    product.save()
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

# Get GHN Services
def get_shipping_service(order_id):
    order = Order.objects.get(pk=order_id)
    seller = order.store
    customer = order.customer
    header = {
        'Content-Type': 'application/json',
        'token': '8ae8d191-18b9-11ed-b136-06951b6b7f89'
    }
    data = {
        "shop_id": 117552,
        "from_district": seller.address.district_id,
        "to_district": customer.address.district_id
    }
    r = json.dumps(data)
    loaded_r = json.loads(r)
    url = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/available-services'
    x = requests.post(url=url, json=loaded_r, headers=header)
    return x.text


# POST request to create shipping order
def create_shipping_order(order_id):
    order = Order.objects.get(pk=order_id)
    seller = order.store
    customer = order.customer
    max_lwh = calculate_max_lwh(order_id=order.id)
    value = 0
    if order.payment_type == 0:
        value = order.bill.value
    service_type_id = 2
    services = json.loads(get_shipping_service(order.id))
    if services.get('code') == 200:
        service_data = services.get('data')
        service_type_id = service_data[0].get('service_type_id')
        service_id = service_data[0].get('service_id')
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
            "return_district_id": seller.address.district_id,
            "return_ward_code": str(seller.address.ward_id),
            "client_order_code": str(order.id),
            "to_name": customer.last_name + " " + customer.first_name,
            "to_phone": customer.phone_number,
            "to_address": customer.address.full_address,
            "to_ward_code": str(customer.address.ward_id),
            "to_district_id": customer.address.district_id,
            "cod_amount": int(value),
            "content": order.note,
            "weight": max_lwh.get('total_weight'),
            "length": max_lwh.get('max_length'),
            "width": max_lwh.get('max_width'),
            "height": max_lwh.get('max_height'),
            "insurance_value": int(value),
            "service_id" : service_id,
            "service_type_id": service_type_id,
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

def increase_unit_in_stock_when_cancel_order(order_id):
    order = Order.objects.get(pk=order_id)
    for odd in order.orderdetail_set.all():
        print(odd.id)
        print(odd.product_option.id)
        try:
            with transaction.atomic():
                op = Option.objects.select_for_update().get(id=odd.product_option.id)
                print(op.unit_in_stock)
                print(odd.quantity)
                op.unit_in_stock = F('unit_in_stock') + odd.quantity
                op.save()
                print("increased unit")
                print(op.unit_in_stock)
        except:
            continue
    return 1

@transaction.atomic
def decrease_user_balance(user_id, value):
    user = User.objects.select_for_update().get(pk=user_id)
    user.balance = F('balance') - value
    user.save()
    return user

@transaction.atomic
def increase_user_balance(user_id, value):
    user = User.objects.select_for_update().get(pk=user_id)
    user.balance = F('balance') + value
    user.save()
    return user

def cancel_order(order_id):
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order_id, status=1)
            order.status = 4
            order.save()
            increase_unit_in_stock_when_cancel_order(order.id)
            if order.bill.payed:
                increase_user_balance(order.customer.id, order.bill.value)
    except:
        return False
    else:
        return True

def recieve_order(order_id):
    try:
        with transaction.atomic():
            order = Order.objects.get(pk=order_id)
            order.status = 3
            increase_user_balance(order.store.id, order.bill.value)
            order.save()
    except:
        return False
    else:
        return True

def checkout_order(order_id, voucher_code=None, payment_type=0, raw_status=1):
    try:
        value = 0
        status = raw_status
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order_id, status=0)
            order.payment_type = payment_type

            voucher = None
            if voucher_code is not None:
                voucher = Voucher.objects.filter(code=voucher_code)
            if voucher is not None and voucher.exists():
                value = calculate_value(order_id=order.id, voucher_id=voucher[0].id)
                if check_discount_in_order(order.orderdetail_set.all(), voucher[0].id) is not None:
                    order.voucher_apply = voucher[0]
            else:
                value = calculate_value(order_id=order.id)
            if payment_type == 2:
                status = 1
                if decrease_user_balance(order.customer.id, value) is None:
                    raise Exception
            order.bill = Bill.objects.create(value=value, order_payed=order, customer=order.customer,
                                             payed=bool(status))

            if payment_type != 1:
                for i in order.orderdetail_set.all():
                    decrease_option_unit_instock(i.id)
            # update status
            order.status = status
            order.save()

    except:
        return None
    else:
        order.refresh_from_db()
        return order

@transaction.atomic
def complete_checkout_orders_with_payment_gateway(order_ids):
    try:
        with transaction.atomic():
            orders = Order.objects.select_for_update().filter(pk__in=order_ids,  status=0, payment_type=1)
            if orders:
                for order in orders:
                    for i in order.orderdetail_set.all():
                        decrease_option_unit_instock(i.id)
                    order.status = 1
                    order.save()
    except:
        return False
    else:
        return True

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
def update_shipping_code(order_id):
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order_id)
            shipping_order = json.loads(create_shipping_order(order_id=order.id))
            if shipping_order.get('code') == 200:
                data = shipping_order.get('data')
                order.shipping_code = data.get('order_code')
                order.total_shipping_fee = data.get('total_fee')
                order.completed_date = shipping_order.get('expected_delivery_time')
            order.can_destroy = False
            order.status = 2
            order.save()
    except:
        return False
    else:
        return True

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

def send_email(reciever, subject, content):
    to = [reciever]
    send_subject = subject
    send_content = content
    return send_mail(send_subject, send_content, settings.EMAIL_HOST_USER, to, False)