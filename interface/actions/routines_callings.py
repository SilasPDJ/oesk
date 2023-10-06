import os
import sys
import clipboard
import subprocess

import pandas as pd

from backend.repository import MainEmpresasRepository, ClientComptsRepository
from interface.settings import AppSettings
from backend.utilities.helpers import modify_dataframe_at, sort_dataframe

from backend.pgdas_fiscal_oesk import *


# Se quiser lidar com os repositories direto dentro da classse de rotina
# vai ter que instanciar eles dentro dos arquivos em pgdas_fiscal_oesk


class RoutinesCallings:
    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings
        self.compt = self.aps.compt
        self.compts_repository = ClientComptsRepository(self.compt)
        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def _generate_all_valores(self, row: pd.Series) -> dict:
        """This will be updated to get all in table"""
        anexo_valores_keys = ['sem_retencao', 'com_retencao', 'anexo']
        valores = {key: row[key] for key in anexo_valores_keys}
        return valores

    def call_gias(self):
        df = self.compts_repository.get_interface_df(allowing_impostos_list='LP')
        # df = self.aps.client_compts_df

        attributes_required = ['razao_social',
                               'ha_procuracao_ecac', "ginfess_cod"]
        required_df = df.loc[:, attributes_required]

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            GIA(*args, compt=self.compt)

            # update declaracao
            orm_row = self.compts_repository.get_as_orm(row)
            if not orm_row.declarado:
                orm_row.declarado = True
                orm_row.envio = True

            self.compts_repository.update_from_object(orm_row)

    def call_giss(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social',
                               'cnpj', 'giss_login']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            GissGui(*args, compt=self.compt)

    def call_ginfess(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social',
                               'cnpj', 'ginfess_cod', 'ginfess_link']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            DownloadGinfessGui(*args, compt=self.compt)

            orm_row = self.compts_repository.get_as_orm(row)

    def call_g5(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'imposto_a_calcular', 'nf_saidas', 'nf_entradas']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            G5(*args, compt=self.compt)

            orm_row = self.compts_repository.get_as_orm(row)

    def call_pgdas_declaracao(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'ha_procuracao_ecac']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()

            PgdasDeclaracao(*args, compt=self.compt, all_valores=self._generate_all_valores(row))
            orm_row = self.compts_repository.get_as_orm(row)
            if not orm_row.declarado:
                orm_row.declarado = True
                self.compts_repository.update_from_object(orm_row)

            # What about to update???
            print()

    def call_send_pgdas_email(self):
        df = self.compts_repository.get_df_to_email()
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'declarado', 'valor_total', 'imposto_a_calcular', 'envio']
        # required_df = df.loc[:, attributes_required]  # type: pd.DataFrame
        for e, row in df.iterrows():
            df_required = row.loc[:, attributes_required]

            PgDasmailSender()

    def call_func_v3(self):
        df = self.aps.client_compts_df
