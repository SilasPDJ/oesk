import os
import sys
from typing import List

import clipboard
import subprocess

import pandas as pd

from backend.repository import MainEmpresasRepository, ClientComptsRepository
from interface.settings import AppSettings
from backend.utilities.helpers import modify_dataframe_at, sort_dataframe

from backend.pgdas_fiscal_oesk import *
from utilities.compt_utils import get_compt


# Se quiser lidar com os repositories direto dentro da classse de rotina
# vai ter que instanciar eles dentro dos arquivos em pgdas_fiscal_oesk

# TODO: fix if not orm_row.declarado

class RoutinesCallings:
    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings
        self.compt = self.aps.compt
        self.compts_repository = ClientComptsRepository(self.compt)
        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def _generate_all_valores(self, row: pd.Series) -> List[dict]:
        """This will be updated to get all in table"""
        anexo_valores_keys = ['sem_retencao', 'com_retencao', 'anexo']
        valores = {key: row[key] for key in anexo_valores_keys}
        return [valores]

    def call_gias(self):
        df = self.compts_repository.get_interface_df(allowing_impostos_list=['LP'])
        # df = self.aps.client_compts_df
        print(self.aps.get_venc_das())
        attributes_required = ['razao_social',
                               # 'ha_procuracao_ecac', "ginfess_cod"]
                               'ha_procuracao_ecac']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            try:
                login, senha = row['ginfess_cod'].split("//")  # Split 'ginfess_cod' once
            except ValueError:
                print(f"\033[1;31m {row['razao_social']} não faz GIA. \033[m")
                continue
            args = row_required.to_list() + [login, senha]

            GIA(*args, compt=self.compt, first_compt=self.compt)
            # set with get_compt util in first_compt when you need more than one

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
            GissGui(args, compt=self.compt, first_compt=get_compt(-2))

    def call_ginfess(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social',
                               'cnpj', 'ginfess_cod', 'ginfess_link']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            if row_required['ginfess_link'] == '':
                continue
            args = row_required.to_list()
            DownloadGinfessGui(*args, compt=self.compt)

            # orm_row = self.compts_repository.get_as_orm(row)

    def call_g5(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'imposto_a_calcular', 'nf_saidas', 'nf_entradas']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            G5(*args, compt=self.compt)

            orm_row = self.compts_repository.get_as_orm(row)
            orm_row.nf_saidas = 'OK'
            self.compts_repository.update_from_object(orm_row)

    def call_pgdas_declaracao(self):
        df = self.aps.client_compts_df
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'ha_procuracao_ecac']
        merged_df_cod_acesso = df.loc[df['ha_procuracao_ecac'] == 'não', :]
        merged_df_proc_ecac = df.loc[df['ha_procuracao_ecac'] == 'sim', :]
        merged_df = pd.concat([merged_df_cod_acesso,merged_df_proc_ecac], ignore_index=True)

        for e, row in merged_df.iterrows():
            if not row['pode_declarar']:
                continue
            else:
                row_required = row[attributes_required]
                args = row_required.to_list()

                orm_row = self.compts_repository.get_as_orm(row)
                PgdasDeclaracao(*args, compt=self.compt, all_valores=self._generate_all_valores(row))
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
            row_required = row[attributes_required]
            orm_row = self.compts_repository.get_as_orm(row)
            if orm_row.envio != 'OK' and orm_row.declarado == 'S':
                PgDasmailSender(*row_required, compt=self.compt, venc_das=self.aps.get_venc_das(), email=row['email'])
                orm_row.envio = 'OK'
                self.compts_repository.update_from_object(orm_row)



    def call_func_v3(self):
        df = self.aps.client_compts_df
