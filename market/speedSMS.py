import requests

endpoint = "https://api.speedsms.vn/index.php/sms/send"
type = 2
sender = "9e2e49fdf026beae"
access_token = "zhu2N-gJRJe6PWdWF_OXfr6-jbNm71gz"

def send_sms(receiver, content):
    params = {
        "to": receiver,
        "content": content,
        "type": str(type),
        "sender": sender,
        "access-token": access_token
    }

    response = requests.get(url=endpoint, params=params)

    return response.json()