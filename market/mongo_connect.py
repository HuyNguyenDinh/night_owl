import pymongo
from pymongo.server_api import ServerApi
from .momo import *
from .models import *

client = pymongo.MongoClient("mongodb+srv://mongodb:0937461321Huy@nightowl.icksujp.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db_payment = client.payment

def import_signature(order_id):
    order = Order.objects.get(pk=order_id)
    momo_collection = db_payment.momo
    payment_result = send_order(order.id)
    add_to_mongo_res = momo_collection.insert_one(payment_result)
    return momo_collection.find_one({"_id": add_to_mongo_res.inserted_id})

def get_instance_from_signature_and_request_id(**kwargs):
    signature = kwargs.get("signature")
    request_id = kwargs.get("requestId")
    momo_order_id = kwargs.get("orderId")
    momo_collection = db_payment.momo
    instance = momo_collection.find_one({"signature": signature, "requestId":  request_id, "orderId": momo_order_id})
    if instance:
        return instance
    return None
