import os
import sys
from typing import List

import clipboard
import subprocess

import pandas as pd

from backend.repository import ClientComptsRepository
from interface.settings import AppSettings
from backend.utilities.helpers import modify_dataframe_at, sort_dataframe

from backend.pgdas_fiscal_oesk import *
from utilities.compt_utils import get_compt
from utilities.default import default_qrcode_driver, pgdas_driver
from utilities.services.empresas_appian_data import set_empresas_appian_data_to_local


# Se quiser lidar com os repositories direto dentro da classse de rotina
# vai ter que instanciar eles dentro dos arquivos em pgdas_fiscal_oesk
# olhar para repository principalmente

class RoutinesCallings:
    # Iniciais dos métodos:
    # `run`: para projetos externos
    # `call`: para rotinas de automação
    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings
        self.compt = self.aps.compt
        self.compts_repository = ClientComptsRepository(self.compt)

        set_empresas_appian_data_to_local()
        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def _generate_all_valores(self, row: pd.Series) -> List[dict]:
        """This will be updated to get all in table"""
        anexo_valores_keys = ['sem_retencao', 'com_retencao', 'anexo']
        valores = {key: row[key] for key in anexo_valores_keys}
        return [valores]

    def call_gias(self):
        df = self.compts_repository.query_data_by_routine_in_compt('gias')
        attributes_required = ['razao_social', 'inscricao_estadual', 'login', 'password']

        for e, row in df.iterrows():
            row_required = row[attributes_required]

            args = row_required.to_list()

            GIA(*args, compt=self.compt, first_compt=self.compt)
            # set with get_compt util in first_compt when you need more than one

            # update declaracao
            if not row['declarado']:
                row['declarado'] = True
                row['envio'] = True

                self.compts_repository.update_from_dictionary(row.to_dict())

    def call_giss(self):
        # df = self.aps.client_compts_df
        df = self.compts_repository.query_data_by_routine_in_compt('iss')
        # Abaixo são as mesmas expressões...
        # df = df.loc[(df['giss_login'] != 'não há') & (df['giss_login'].str.lower() != 'ginfess cód') & (
        #             df['giss_login'] != '')].fillna('')
        df = df.loc[~df['giss_login'].str.lower().isin(['não há', 'ginfess cód', ''])].fillna('')
        df = df.loc[df['gissonline'].str.lower() == 'https://portal.gissonline.com.br/login/index.html']
        # ...
        attributes_required = ['razao_social',
                               'cnpj', 'giss_login']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            GissGui(args, compt=self.compt, headless=False)

    def call_ginfess(self):
        # df = self.aps.client_compts_df
        # TODO: substituir por nova tabela propria do giss, pois o giss tem pra icms e iss, e sem mov
        df = self.compts_repository.query_data_by_routine_in_compt('iss')

        df['nfs_login_link'] = df['nfs_login_link'].fillna('').astype(str)

        attributes_required = ['razao_social',
                               'login', 'password', 'nfs_login_link']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            if row_required['nfs_login_link'] == '' or row_required['nfs_login_link'].lower() == 'não há':
                print(f'\nGinfess pula {row["razao_social"]}')
                continue
            try:
                args = row_required.to_list()
                dgg = DownloadGinfessGui(*args, compt=self.compt)
            except Exception as e:
                print("\033[1;33mNão foi possível conferir...\033[m", row_required.values)
                print("Pulando por enquanto...")
                continue
            else:
                row['pode_declarar'] = True
                if dgg.ginfess_valores:
                    self.compts_repository.update_from_dictionary(row.to_dict() |
                                                                  {key: dgg.ginfess_valores[key_indx] for key_indx, key
                                                                   in
                                                                   enumerate(
                                                                       ["sem_retencao", "com_retencao", "valor_total"])
                                                                   } if dgg.ginfess_valores else None)
                else:
                    self.compts_repository.update_from_dictionary(row.to_dict())

    def call_g5(self):
        # df = self.aps.client_compts_df
        df = self.compts_repository.query_data_by_routine_in_compt('iss')
        # df = self.compts_repository.query_data_by_routine_in_compt('icms')

        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'imposto_a_calcular', 'nf_saidas', 'nf_entradas']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            G5(*args, compt=self.compt)

            row['nf_saidas'] = 'OK'
            self.compts_repository.update_from_dictionary(row.to_dict())

    def call_pgdas_declaracao(self):
        # df = self.aps.client_compts_df
        df = self.compts_repository.get_interface_df()
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'ha_procuracao_ecac']
        merged_df_cod_acesso = df.loc[df['ha_procuracao_ecac'] == 'não', :]
        merged_df_proc_ecac = df.loc[df['ha_procuracao_ecac'] == 'sim', :]
        merged_df = pd.concat([merged_df_cod_acesso, merged_df_proc_ecac], ignore_index=True)

        # ecac_driver = default_qrcode_driver('C:\\Temp')
        ecac_driver = pgdas_driver()
        # TODO: pressionar f9 somente 1x p/ prosseugir
        for e, row in merged_df.iterrows():
            if not row['pode_declarar']:
                continue
            else:
                row_required = row[attributes_required]
                args = row_required.to_list()

                if row['ha_procuracao_ecac'] == 'sim':
                    PgdasDeclaracao(*args, compt=self.compt, all_valores=self._generate_all_valores(row),
                                    driver=ecac_driver)
                else:
                    PgdasDeclaracao(*args, compt=self.compt, all_valores=self._generate_all_valores(row))

                row['declarado'] = True
                self.compts_repository.update_from_dictionary(row.to_dict())

            # What about to update???
            print()

    def call_jr(self):
        df = self.compts_repository.query_data_by_routine_in_compt('icms')
        attributes_required = ['razao_social', 'cnpj']
        for e, row in df.iterrows():
            if row['valor_total'] != 0:
                continue
            row_required = row[attributes_required]
            args = row_required.to_list()
            JR(*args, compt=self.compt)

    def call_send_pgdas_email(self):
        df = self.compts_repository.query_data_by_routine_in_compt('todas', must_be_authorized=True)
        df = df.loc[~df['envio']]
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'declarado', 'valor_total', 'imposto_a_calcular', 'envio']
        # required_df = df.loc[:, attributes_required]  # type: pd.DataFrame
        for e, row in df.iterrows():
            row_required = row[attributes_required]
            if not row['envio'] and row['declarado']:
                PgDasmailSender(*row_required, compt=self.compt, venc_das=row['venc_das'] or self.aps.get_venc_das(),
                                email=row['email'])
                row['envio'] = True
                self.compts_repository.update_from_dictionary(row.to_dict())

    def run_oesk_project_excel(self):

        subprocess.Popen("O:\\HACKING\\MY_PROJECTS\\oesk\\backend\\utilities\\scripts\\run_react_project.bat")

    def call_func_v3(self):
        df = self.aps.client_compts_df
