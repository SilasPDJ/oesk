import os
import time
from datetime import datetime as dt
import requests
from credentials.appian import get_token

def acessar_api(url: str, token: str, params: {}):
    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("GET", url, params=params, headers=headers, data=payload)

    print(response.text)
    return response.json


# params = {'empresa_id': 10}
params = {}

response = acessar_api(url='https://cvjn.appian.community/suite/webapi/ICd5WQ', token=get_token(), params=params)
print(response)
# Primeira API Appian
