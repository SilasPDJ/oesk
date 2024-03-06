import os
import time
from datetime import datetime as dt
from typing import List

import requests
from credentials.appian import get_token
from api import acessar_api_default
from dotenv import load_dotenv

from repository import OeGiasRepository, OeServicosRepository, OeEmpresasRepository

load_dotenv()


# params = {'empresa_id': 10}
API = os.getenv("APPIAN_EMPRESAS_API")


def set_empresas_appian_data_to_local():
    token = get_token()
    servicos = acessar_api_default(url=API, token=token, params={'tipo_empresa': 'iss'})
    gias = acessar_api_default(url=API, token=token, params={'tipo_empresa': 'gias'})
    # outras = acessar_api_default(url=API, token=token, params={'tipo_empresa': 'outras'})
    todas = acessar_api_default(url=API, token=token, params={'tipo_empresa': 'todas'})
    print()

    oe_geral = OeEmpresasRepository()
    oe_servicos = OeServicosRepository()
    oe_gias = OeGiasRepository()

    oe_geral.insert_objects_if_not_exist(todas)
    oe_servicos.insert_objects_if_not_exist(servicos)
    oe_gias.insert_objects_if_not_exist(gias)

# Primeira API Appian
