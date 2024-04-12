import os
import time
from datetime import datetime as dt
from typing import List, Union
from utilities.compt_utils import get_compt, compt_to_date_obj
import requests
from utilities.services.credentials.appian import get_token
from utilities.services.api import acessar_api_default
from dotenv import load_dotenv

from repository import OeGiasRepository, OeServicosRepository, OeEmpresasRepository, OeICMSRepository
from repository import OeComptsValoresImpostosRepository, OeClientComptsRepository
from dateutil.relativedelta import relativedelta
from datetime import datetime
from repository.utils import to_camel_case

load_dotenv()

# params = {'empresa_id': 10}
API_URL = os.getenv("APPIAN_API_URL")

EMPRESAS_URL = API_URL + 'ICd5WQ'
COMPTS_URL = API_URL + 'get_compts_dados'
COMPT_UPDATE_URL = API_URL + 'update_compts'
COMPT_VALORES_UPDATE_URL = API_URL + 'wo4tXQ'


def set_empresas_appian_data_to_local():
    token = get_token()
    servicos = acessar_api_default(url=EMPRESAS_URL, token=token, params={'tipo_empresa': 'iss'})
    gias = acessar_api_default(url=EMPRESAS_URL, token=token, params={'tipo_empresa': 'gias'})
    outras_icms = acessar_api_default(url=EMPRESAS_URL, token=token, params={'tipo_empresa': 'outras'})
    todas = acessar_api_default(url=EMPRESAS_URL, token=token, params={'tipo_empresa': 'todas'})

    print()

    oe_geral = OeEmpresasRepository()
    oe_servicos = OeServicosRepository()
    oe_gias = OeGiasRepository()
    oe_icms_semmov = OeICMSRepository()

    oe_geral.insert_objects_if_not_exist(todas)
    oe_servicos.insert_objects_if_not_exist(servicos)
    oe_gias.insert_objects_if_not_exist(gias)
    oe_icms_semmov.insert_objects_if_not_exist(outras_icms)


# Primeira API Appian
def _get_compts_data_from_appian(cont=-1):
    token = get_token()
    compts = acessar_api_default(url=COMPTS_URL, token=token, params={'compt': get_compt(cont)})
    print(compts)
    return compts


def set_compt_appian_data_to_local():
    """
    Creates new compt in appian if not exists
    :return:
    """
    token = get_token()

    def get_status_imports_g5(
            campo: str):
        campo = '' if campo is None else campo
        return campo if campo.upper() != 'OK' else ''

    compts_previous_data = _get_compts_data_from_appian(2)

    compts_exist_length = len(_get_compts_data_from_appian(1))

    if compts_exist_length == len(compts_previous_data):
        print('Compt already exists, passing...')
        return

    oe_valores = OeComptsValoresImpostosRepository()
    oe_compts = OeClientComptsRepository(get_compt())

    for e, row in enumerate(compts_previous_data):
        if e <= compts_exist_length:
            continue
        # row['comptsValoresImpostos'] = row['comptsValoresImpostos'][0]
        new_row: dict = row.copy()
        new_row.pop('id')

        new_row['envio'] = False
        new_row['podeDeclarar'] = False
        new_row['declarado'] = False
        new_row['compt'] = (datetime.strptime(new_row['compt'], '%Y-%m-%dZ') + relativedelta(months=1)).strftime(
            '%Y-%m-%dZ')
        new_row['venc_das'] = datetime.strptime(new_row['venc_das'], '%Y-%m-%dZ')

        new_row.pop('empresasAll')
        valores = new_row.pop('comptsValoresImpostos')
        print(valores)

        created_compt = acessar_api_default(method="POST", url=COMPT_UPDATE_URL, token=token, data=new_row)

        if isinstance(valores, list):
            for i in range(len(valores)):
                valores[i].pop('id')
                valores[i]['valorTotal'] = 0
                valores[i]['semRetencao'] = 0
                valores[i]['comRetencao'] = 0
                valores[i]['nfSaidaPrestador'] = get_status_imports_g5(valores[i]['nfSaidaPrestador'])
                valores[i]['nfEntradaTomador'] = get_status_imports_g5(valores[i]['nfEntradaTomador'])

                valores[i]['idClientCompt'] = created_compt[0]['id']

                status = acessar_api_default(method="POST", url=COMPT_VALORES_UPDATE_URL, token=token, data=valores[i])
                print('creating: ', status)

        oe_compts.insert_objects_if_not_exist([new_row])
        oe_valores.insert_objects_if_not_exist(valores)


def send_clients_compts_update(compt_data: Union[dict, list]):
    compt_data = to_camel_case(compt_data)
    token = get_token()
    # data = get_compts_data_from_appian(-2)
    status_compt = acessar_api_default(method="POST", url=COMPT_UPDATE_URL, token=token, data=compt_data)
    print('updating compt: ', status_compt)

    return bool(status_compt)


def send_compts_valores_update(valores_data: Union[dict, list]):
    valores_data = to_camel_case(valores_data)
    token = get_token()
    status = acessar_api_default(method="POST", url=COMPT_VALORES_UPDATE_URL, token=token, data=valores_data)
    print('updating valores: ', status)

    return bool(status)


def ____maior_id_menor_id():
    compts_data = _get_compts_data_from_appian(2)
    maior = menor = 0
    for row in compts_data:
        test = row['comptsValoresImpostos']

        num1 = test[0]['id']
        num2 = test[1]['id']
        print(num1, ' ', num2)

        if menor == 0:
            menor = num1
        if num2 > maior:
            maior = num2

        if num2 < menor:
            menor = num2
    print(maior, ' ', menor)


if __name__ == '__main__':
    set_compt_appian_data_to_local()

    # TODO: ids not in new_ids and not in existing_ids, desativar (GIAS), a api ta retornando bem...
    # TODO, empresa precisa tar ativa pra estar ativa na GIA???
    set_empresas_appian_data_to_local()
print('finish')
