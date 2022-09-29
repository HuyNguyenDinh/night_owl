import json
import urllib.request
import urllib
import uuid
import requests
import hmac
import hashlib
from .models import *
import pymongo
from pymongo.server_api import ServerApi
from datetime import datetime

client = pymongo.MongoClient("mongodb+srv://mongodb:0937461321Huy@nightowl.icksujp.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db_payment = client.payment

# parameters send to MoMo get get payUrl
partnerCode = "MOMO"
accessKey = "F8BBA842ECF85"
secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
secretLink = str(uuid.uuid4())

def send_order(orders_id, redirect_url):
    orders = Order.objects.filter(pk__in=orders_id)
    raw_amount = list(orders.values_list('bill__value', flat=True))
    order_amount = sum(raw_amount)
    order_ids = list(set(orders.values_list('id', flat=True)))
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    orderInfo = "Night Owl order"
    redirectUrl = redirect_url
    ipnUrl = "https://night-owl-market.herokuapp.com/market/momo-payed/" + secretLink + "/"
    amount = str(int(order_amount))
    orderId = "Night_Owl:" + str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    requestType = "captureWallet"
    extraData = ""  # pass empty value or Encode base64 JsonString

    # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
    # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
    # &requestType=$requestType
    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

    # puts raw signature
    # signature
    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()

    # json object send to MoMo endpoint

    data = {
        'partnerCode': partnerCode,
        'partnerName': "Test",
        'storeId': "MomoTestStore",
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': redirectUrl,
        'ipnUrl': ipnUrl,
        'lang': "vi",
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature
    }
    loaded_data = json.dumps(data)


    clen = len(data)
    response = requests.post(endpoint, data=loaded_data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    response_json = response.json()

    res = dict(response_json, **{"secretLink": secretLink, "order_ids": order_ids, "type": 0})
    return res

def cashin_balance(user_id, raw_amount, redirect_url):
    user = User.objects.get(pk=user_id)
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    orderInfo = "Night Owl cashin"
    redirectUrl = redirect_url
    ipnUrl = "https://night-owl-market.herokuapp.com/market/momo-payed/" + secretLink + "/"
    amount = str(raw_amount)
    orderId = "Night_Owl:" + str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    requestType = "captureWallet"
    extraData = ""  # pass empty value or Encode base64 JsonString

    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

    # puts raw signature
    # signature
    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()

    data = {
        'partnerCode': partnerCode,
        'partnerName': "Test",
        'storeId': "MomoTestStore",
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': redirectUrl,
        'ipnUrl': ipnUrl,
        'lang': "vi",
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature
    }
    loaded_data = json.dumps(data)
    clen = len(data)
    response = requests.post(endpoint, data=loaded_data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    response_json = response.json()

    res = dict(response_json, **{"secretLink": secretLink, "user_id": user.id, "type": 1})
    return res

def check_momo_order_status(order_id, request_id):
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/query"
    orderId = order_id
    requestId = request_id

    rawSignature = "accessKey=" + accessKey + "&orderId=" + orderId + "&partnerCode=" + partnerCode + "&requestId=" + requestId
    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()

    data = {
        'partnerCode': partnerCode,
        'requestId': requestId,
        'orderId': orderId,
        'lang': "vi",
        'signature': signature
    }

    loaded_data = json.dumps(data)
    clen = len(data)
    response = requests.post(endpoint, data=loaded_data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    return response.json()

def momo_refund(trans_id, amount, request_id):
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/refund"
    orderId = str(uuid.uuid4())
    requestId = request_id
    amount = str(amount)
    description = "Refund Night Owl orders"
    transId = str(trans_id)

    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&description=" + description + "&orderId=" + orderId + "&partnerCode=" + partnerCode + "&requestId=" + requestId + "&transId=" + transId
    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()

    data = {
        'partnerCode': partnerCode,
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'lang': "vi",
        'transId': transId,
        'description': description,
        'signature': signature
    }
    loaded_data = json.dumps(data)
    clen = len(data)
    response = requests.post(endpoint, data=loaded_data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    return response.json()