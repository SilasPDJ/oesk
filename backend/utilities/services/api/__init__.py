import requests


def acessar_api_default(url: str, token: str, params: {}):
    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("GET", url, params=params, headers=headers, data=payload)

    print(response.text)
    return response.json()
