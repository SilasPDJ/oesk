import os
import sys
import clipboard
import subprocess

import pandas as pd

from backend.repository import MainEmpresasRepository, ClientComptsRepository
from interface.settings import AppSettings

from backend.pgdas_fiscal_oesk import *


class RoutinesCallings:
    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings

        self.compts_repository = ClientComptsRepository(self.aps.compt)
        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def call_gias(self):
        df = self.compts_repository.get_interface_df(allowing_impostos_list='LP')
        # df = self.aps.client_compts_df

        attributes_required = ['razao_social',
                               'ha_procuracao_ecac', "ginfess_cod"]
        required_df = df.loc[:, attributes_required]


    def call_giss(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social',
                               'cnpj', 'giss_login']
        required_df = df.loc[:, attributes_required]


    def call_ginfess(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social',
                               'cnpj', 'ginfess_cod', 'ginfess_link']
        required_df = df.loc[:, attributes_required]

    def call_g5(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'imposto_a_calcular', 'nf_saidas', 'nf_entradas']
        required_df = df.loc[:, attributes_required]

    def call_simples_nacional(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'ha_procuracao_ecac']
        anexo_valores_keys = ['sem_retencao', 'com_retencao', 'anexo']

        required_df = df.loc[:, attributes_required]
    def call_send_pgdas_email(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'declarado', 'valor_total', 'imposto_a_calcular', 'envio']
        required_df = df.loc[:, attributes_required]



    def call_func_v3(self):
        df = self.aps.client_compts_df

