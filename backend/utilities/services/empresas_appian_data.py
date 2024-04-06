import os
import time
from datetime import datetime as dt
from typing import List
from utilities.compt_utils import get_compt, compt_to_date_obj
import requests
from utilities.services.credentials.appian import get_token
from utilities.services.api import acessar_api_default
from dotenv import load_dotenv

from repository import OeGiasRepository, OeServicosRepository, OeEmpresasRepository, OeICMSRepository
from dateutil.relativedelta import relativedelta
from datetime import datetime

load_dotenv()

# params = {'empresa_id': 10}
API_URL = os.getenv("APPIAN_API_URL")

empresas_url = API_URL + 'ICd5WQ'
compts_url = API_URL + 'get_compts_dados'
update_compt_url = API_URL + 'update_compts'
update_compt_valores_url = API_URL + 'wo4tXQ'


def set_empresas_appian_data_to_local():
    token = get_token()
    servicos = acessar_api_default(url=empresas_url, token=token, params={'tipo_empresa': 'iss'})
    gias = acessar_api_default(url=empresas_url, token=token, params={'tipo_empresa': 'gias'})
    outras_icms = acessar_api_default(url=empresas_url, token=token, params={'tipo_empresa': 'outras'})
    todas = acessar_api_default(url=empresas_url, token=token, params={'tipo_empresa': 'todas'})

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


def get_compts_data_from_appian(cont=-1):
    token = get_token()
    compts = acessar_api_default(url=compts_url, token=token, params={'compt': get_compt(cont)})
    print(compts)
    return compts


def update_compt():
    token = get_token()
    # data = get_compts_data_from_appian(-2)
    data = []
    status = acessar_api_default(method="POST", url=update_compt_url, token=token, data=data)
    print(status)
    return status


def maior_id_menor_id():
    compts_data = get_compts_data_from_appian(2)
    maior = menor = 0
    # TODO DELETAR ids comptsValoresImpostos: 2126, 2057 (duplicados)
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


def create_new_compt():
    token = get_token()

    compt = compt_to_date_obj(get_compt())

    def get_status_imports_g5(
            campo: str):
        campo = '' if campo is None else campo
        return campo if campo.upper() != 'OK' else ''

    compts_data = get_compts_data_from_appian(2)

    compts_exist_len = len(get_compts_data_from_appian(1))

    if compts_exist_len == len(compts_data):
        return

    for e, row in enumerate(compts_data):
        if e <= compts_exist_len:
            continue
        # row['comptsValoresImpostos'] = row['comptsValoresImpostos'][0]
        new_row: dict = row.copy()
        new_row.pop('id')

        new_row['envio'] = False
        new_row['podeDeclarar'] = False
        new_row['declarado'] = False
        new_row['compt'] = (datetime.strptime(new_row['compt'], '%Y-%m-%dZ') + relativedelta(months=1)).strftime(
            '%Y-%m-%dZ')

        new_row.pop('empresasAll')
        valores = new_row.pop('comptsValoresImpostos')
        print(valores)

        created_compt = acessar_api_default(method="POST", url=update_compt_url, token=token, data=new_row)

        if isinstance(valores, list):
            # new_row['comptsValoresImpostos'] = new_row['comptsValoresImpostos'][0]
            for i in range(len(valores)):
                valores[i].pop('id')
                valores[i]['valorTotal'] = 0
                valores[i]['semRetencao'] = 0
                valores[i]['comRetencao'] = 0
                valores[i]['idClientCompt'] = created_compt[0]['id']

                status = acessar_api_default(method="POST", url=update_compt_valores_url, token=token, data=valores[i])
                print('status')


if __name__ == '__main__':
    # on_update()
    create_new_compt()

    # TODO: ids not in new_ids and not in existing_ids, desativar (GIAS), a api ta retornando bem...
    # TODO, empresa precisa tar ativa pra estar ativa na GIA???
    # TODO update não está funcionando, ele não está atualizando de acordo... no utils de repository
    set_empresas_appian_data_to_local()
print('finish')
