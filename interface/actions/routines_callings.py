import os
import sys
from datetime import datetime
from typing import List, Tuple, Union, Any

import clipboard
import subprocess

import pandas as pd

from backend.repository import OeClientComptsRepository as ClientComptsRepository
from interface.settings import AppSettings
from backend.utilities.helpers import modify_dataframe_at, sort_dataframe

from backend.pgdas_fiscal_oesk import *
from utilities.compt_utils import get_compt
from utilities.default import default_qrcode_driver, pgdas_driver
from utilities.services.empresas_appian_data import set_empresas_appian_data_to_local, set_compt_appian_data_to_local
from utilities.services.empresas_appian_data import update_compt, update_valores


# Se quiser lidar com os repositories direto dentro da classse de rotina
# vai ter que instanciar eles dentro dos arquivos em pgdas_fiscal_oesk
# olhar para repository principalmente

class RoutinesCallings:
    # Iniciais dos métodos:
    # `run`: para projetos externos
    # `call`: para rotinas de automação
    # Automações com driver teoricamente podem ser quebradas e continuar...

    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings
        self.compt = self.aps.compt
        self.compts_repository = ClientComptsRepository(self.compt)

        set_empresas_appian_data_to_local()
        set_compt_appian_data_to_local()
        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def _generate_all_valores(self, row: pd.Series) -> tuple[Union[int, float], list[tuple[float, float, str]]]:
        """This will be updated to get all in table"""
        valores_correspondentes = [(item.get('sem_retencao'), item.get('com_retencao'), item.get('anexo')) for item in
                                   row]
        valor_total = sum([item.get('valor_total') for item in row])
        assert valor_total == row[0]['valor_total']
        return valor_total, valores_correspondentes

    def _update_cloud(self, row):
        row_compt = row
        if row_compt['venc_das']:
            row_compt['venc_das'] = row_compt['venc_das'].strftime('%Y-%m-%dZ')

        row_compt['compt'] = row_compt['compt'].strftime('%Y-%m-%dZ')
        try:
            row_vals = row.pop('comptsValoresImpostos')
            for val in row_vals:
                update_valores(val)
        except Exception as e:
            print(row['razao_social'], 'Não atualizou valores na cloud')
        try:
            update_compt(row_compt.to_dict())
        except Exception as e:
            print(e, 'erro ao atualizar a compt de', row['razao_social'])
        # update_compt()
        # update_valores

    def call_gias(self):
        df = self.compts_repository.query_data_by_routine_in_compt('gias')
        attributes_required = ['razao_social', 'inscricao_estadual', 'login', 'password']

        for e, row in df.iterrows():
            row_required = row[attributes_required]

            args = row_required.to_list()
            try:
                GIA(*args, compt=self.compt, first_compt='11-2023')
                # set with get_compt util in first_compt when you need more than one
            except Exception as e:
                print(args)
                raise e
            else:
                # update declaracao
                if not row['declarado']:
                    row['declarado'] = True
                    row['envio'] = True

                    self.compts_repository.update_from_dictionary(row.to_dict())
                    self._update_cloud(row)

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
            try:
                GissGui(args, compt=self.compt, headless=False)
            except Exception as e:
                print(args, e)
                # raise e

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
                print("Pulando por enquanto...", e)
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
                self._update_cloud(row)

    def call_g5(self):
        # df = self.aps.client_compts_df
        df = self.compts_repository.query_data_by_routine_in_compt('iss')
        # df = self.compts_repository.query_data_by_routine_in_compt('icms')

        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'valor_total', 'imposto_a_calcular', 'nf_saida_prestador',
                               'nf_entrada_tomador']

        for e, row in df.iterrows():
            row_required = row[attributes_required]
            args = row_required.to_list()
            try:
                G5(*args, compt=self.compt)
            except Exception as e:
                print(args)
                raise e
            else:
                row['nf_saidas'] = 'OK'
                self.compts_repository.update_from_dictionary(row.to_dict())
                self._update_cloud(row)

    def call_pgdas_declaracao(self):
        # df = self.aps.client_compts_df
        # df = self.compts_repository.get_interface_df()
        df = self.compts_repository.query_data_by_routine_in_compt('todas')
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'ha_procuracao_ecac']
        merged_df_cod_acesso = df.loc[df['ha_procuracao_ecac'] == 'não', :]
        merged_df_proc_ecac = df.loc[df['ha_procuracao_ecac'] == 'sim', :]
        merged_df = pd.concat([merged_df_cod_acesso, merged_df_proc_ecac], ignore_index=True)

        # ecac_driver = default_qrcode_driver('C:\\Temp')
        ecac_driver = pgdas_driver()
        # TODO: pressionar f9 somente 1x p/ prosseugir
        for e, row in merged_df.iterrows():
            imposto = row['comptsValoresImpostos'][0]['imposto_a_calcular']
            if not row['pode_declarar'] and imposto != 'SEM_MOV':
                continue
            else:
                valor_total, all_valores = self._generate_all_valores(row['comptsValoresImpostos'])
                row_required = row[attributes_required]
                args = row_required.to_list()
                args.insert(-1, valor_total)
                try:
                    if row['ha_procuracao_ecac'] == 'sim':
                        PgdasDeclaracao(*args, compt=self.compt, all_valores=all_valores,
                                        driver=ecac_driver)
                    else:
                        PgdasDeclaracao(*args, compt=self.compt, all_valores=all_valores)

                except Exception as e:
                    print(f'Failed: {row["razao_social"]}')
                else:
                    row['declarado'] = True
                    self.compts_repository.update_from_dictionary(row.to_dict())
                    self._update_cloud(row)

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
        df = self.compts_repository.query_data_by_routine_in_compt('todas')
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
                self._update_cloud(row)

    def run_oesk_project_excel(self):

        subprocess.Popen("O:\\HACKING\\MY_PROJECTS\\oesk\\backend\\utilities\\scripts\\run_react_project.bat")
