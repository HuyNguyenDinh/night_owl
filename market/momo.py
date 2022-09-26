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

client = pymongo.MongoClient("mongodb+srv://mongodb:0937461321Huy@nightowl.icksujp.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db_payment = client.payment
# parameters send to MoMo get get payUrl
def send_order(order_id):
    order = Order.objects.get(pk=order_id)
    items = []
    for odd in order.orderdetail_set.all():
        item = {
            'id': str(odd.id),
            'name': odd.product_option.base_product.name,
            'price': int(odd.unit_price),
            'currency': 'VND',
            'quantity': odd.quantity,
            'total_price': int(odd.unit_price * odd.quantity)
        }
        items.append(item)
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    partnerCode = "MOMO"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    orderInfo = str(order.id)
    redirectUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
    ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
    amount = str(int(order.bill.value))
    orderId = str(uuid.uuid4())
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
        'items': items,
        'signature': signature
    }
    loaded_data = json.dumps(data)


    clen = len(data)
    response = requests.post(endpoint, data=loaded_data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    response_json = response.json()

    res = dict(response_json, **{"order_id": order.id, "signature": data.get("signature")})
    return res
