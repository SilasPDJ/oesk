import os
import requests
from dotenv import load_dotenv


load_dotenv()
CLIENT_ID = os.getenv("appian_client_id")
CLIENT_SECRET = os.getenv("appian_client_secret")
TOKEN_URL = os.getenv("appian_token_url")


def get_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
    # Client ID e Client Secret

    # Parâmetros da solicitação de token
    params = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    # Fazendo a solicitação de token
    response = requests.post(TOKEN_URL, data=params)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Extraindo o token de acesso do corpo da resposta
        token = response.json()["access_token"]
        # print("Token de acesso:", token)
        return token
    else:
        print("Erro ao obter token de acesso:", response.text)
        return ''
