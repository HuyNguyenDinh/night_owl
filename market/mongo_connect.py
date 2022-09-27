import pymongo
from pymongo import ReturnDocument
from pymongo.server_api import ServerApi
from .momo import *
from .models import *
from django.db.models import Sum, F

client = pymongo.MongoClient("mongodb+srv://mongodb:0937461321Huy@nightowl.icksujp.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db_payment = client.payment

def import_signature(order_ids):
    orders = Order.objects.filter(pk__in=order_ids)
    momo_collection = db_payment.momo
    order_ids = list(set(orders.values_list('id', flat=True)))
    amount = []
    for order in orders:
        amount.append(order.bill.value)
    payment_result = send_order(orders_id=order_ids, redirect_url="https://night-owl-market-fe.vercel.app/")
    order_info = momo_collection.find_one({"order_ids": order_ids})
    if order_info:
        return momo_collection.find_one_and_update(order_info, {"$set": payment_result}, return_document=ReturnDocument.AFTER)
    add_to_mongo_res = momo_collection.insert_one(payment_result)
    return momo_collection.find_one({"_id": add_to_mongo_res.inserted_id})

def get_instance_from_signature_and_request_id(**kwargs):
    secret_link = kwargs.get("secret_link")
    request_id = kwargs.get("requestId")
    momo_order_id = kwargs.get("orderId")
    momo_collection = db_payment.momo
    instance = momo_collection.find_one({"secretLink": secret_link, "requestId":  request_id, "orderId": momo_order_id})
    if instance:
        return instance
    return None
