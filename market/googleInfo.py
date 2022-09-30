from google.auth.transport import requests
from google.oauth2 import id_token

def get_user_info(idToken):
    user_info = id_token.verify_oauth2_token(idToken, requests.Request())
    if 'accounts.google.com' in user_info.get('iss'):
        return user_info
    else:
        return None