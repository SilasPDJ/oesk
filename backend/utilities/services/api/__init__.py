import json

import requests
from typing import Union


def _validate_dict_param(arg: Union[dict, None]) -> dict: return dict() if not arg else arg


def _execute_request(method, url, params=None, data=None, headers=None):
    if method == "GET":
        return requests.request(method, url, params=params, headers=headers, data=data)
    elif method == "POST":
        return requests.post(url, headers=headers, params=params, json=data)
    else:
        return {"text": ''}


def acessar_api_default(url: str, token: str, method="GET", params=None, data=None, headers=None):
    params = _validate_dict_param(params)
    data = _validate_dict_param(data)

    headers = {
        'Authorization': f'Bearer {token}',
        **_validate_dict_param(headers)
    }
    response = _execute_request(method, url, params=params, data=data, headers=headers)
    print(response.text)
    try:
        return response.json()
    except Exception as e:
        return response


if __name__ == '__main__':
    test = _validate_dict_param({1: "a"})
    test2 = _validate_dict_param(None)
    # test3 = validate_dict_param("")
    print(test)
    print(test2)
    # print(test3)
