import json
import requests

access_token = "8ae8d191-18b9-11ed-b136-06951b6b7f89"
base_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/"

def get_province_by_id(province_id):
    header = {
        "Content-Type": "application/json",
        "Token": access_token
    }

    url = base_url + "province"
    request = requests.get(url=url, headers=header)
    response = request.json()
    data = response.get('data')
    for province in data:
        if province.get('ProvinceID') == province_id:
            return province.get('ProvinceName')

def get_district_by_id(district_id, province_id):
    header = {
        "Content-Type": "application/json",
        "Token": access_token
    }
    url = base_url + "district"
    body = {
        "province_id": province_id
    }
    request = requests.get(url=url, headers=header, json=body)
    response = request.json()
    data = response.get('data')
    for district in data:
        if district.get('DistrictID') == district_id and district.get('ProvinceID') == province_id:
            return district.get('DistrictName')

def get_ward_by_code(ward_code,district_id):
    header = {
        "Content-Type": "application/json",
        "Token": access_token
    }
    url = base_url + "ward?district_id"
    body = {
        "district_id": district_id
    }
    request = requests.get(url=url, headers=header, json=body)
    response = request.json()
    data = response.get('data')
    for ward in data:
        if ward.get('WardCode') == ward_code and ward.get('DistrictID') == district_id:
            return ward.get('WardName')

