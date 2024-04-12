import os
import sys
from datetime import datetime
from typing import List, Tuple, Union, Any

import clipboard
import subprocess

import pandas as pd

from backend.repository import OeClientComptsRepository as ClientComptsRepository
from backend.repository import OeComptsValoresImpostosRepository
from interface.settings import AppSettings
from backend.utilities.helpers import modify_dataframe_at, sort_dataframe

from backend.pgdas_fiscal_oesk import *
from utilities.compt_utils import get_compt
from utilities.default import default_qrcode_driver, pgdas_driver
from utilities.services.empresas_appian_data import set_empresas_appian_data_to_local, set_compt_appian_data_to_local
from utilities.services.empresas_appian_data import send_clients_compts_update, send_compts_valores_update


# Se quiser lidar com os repositories direto dentro da classse de rotina
# vai ter que instanciar eles dentro dos arquivos em pgdas_fiscal_oesk
# olhar para repository principalmente

class RoutinesCallings:
    # Iniciais dos métodos:
    # `run`: para projetos externos
    # `call`: para rotinas de automação
    # `send`: para chamadas de endpoint

    # Automações com driver teoricamente podem ser quebradas e continuar...
    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings
        self.compt = self.aps.compt
        self.compts_repository = ClientComptsRepository(self.compt)
        self.valores_repository = OeComptsValoresImpostosRepository()

        set_empresas_appian_data_to_local()
        set_compt_appian_data_to_local()
        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def _generate_all_valores(self, row: pd.Series) -> tuple[Union[int, Any], list[dict]]:
        """This will be updated to get all in table"""
        valores_correspondentes = [{chave: item[chave] for chave in ['sem_retencao', 'com_retencao', 'anexo']} for item
                                   in row]
        valor_total = sum([item.get('valor_total') for item in row])
        assert valor_total == row[0]['valor_total']
        return valor_total, valores_correspondentes

    def _run_update_cloud(self, row, shall_update_valores=False):
        from repository.utils import to_camel_case

        row_compt = row.to_dict()

        if row_compt['venc_das']:
            row_compt['venc_das'] = row_compt['venc_das'].strftime('%Y-%m-%dZ')

        row_compt['compt'] = row_compt['compt'].strftime('%Y-%m-%dZ')
        if shall_update_valores:
            try:
                row_vals = row.pop('comptsValoresImpostos')
                for val in row_vals:
                    if not val['nf_saida_prestador']:
                        val['nf_saida_prestador'] = ''
                    if not val['nf_entrada_tomador']:
                        val['nf_saida_prestador'] = ''
                    print(val)
                    send_compts_valores_update(val)
            except Exception as e:
                print(row['razao_social'], 'Não atualizou valores na cloud')
        try:
            del row_compt['razao_social']
            del row_compt['cnpj']
            del row_compt['cpf']
            del row_compt['email']
            send_clients_compts_update(row_compt)
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
                # GIA(*args, compt=self.compt, first_compt='11-2023')
                GIA(*args, compt=self.compt)
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
                    self._run_update_cloud(row)

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
            valores_required = row['comptsValoresImpostos'][0]

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
                    self.compts_repository.update_from_dictionary(row.to_dict())
                    ginfess_valores = {key: dgg.ginfess_valores[key_indx] for key_indx, key
                                       in
                                       enumerate(
                                           ["sem_retencao", "com_retencao", "valor_total"])
                                       }
                    valores_required.update(ginfess_valores)
                    self.valores_repository.update_from_dictionary(valores_required)
                else:
                    self.compts_repository.update_from_dictionary(row.to_dict())
                self._run_update_cloud(row, shall_update_valores=True)

    def call_g5(self):
        # df = self.aps.client_compts_df
        df = self.compts_repository.query_data_by_routine_in_compt('iss')
        # df = self.compts_repository.query_data_by_routine_in_compt('icms')

        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples']
        attributes_required_comptsvals = ['imposto_a_calcular', 'nf_saida_prestador', 'nf_entrada_tomador']

        for e, row in df.iterrows():
            row_required = row[attributes_required]

            args = row_required.to_list()
            args.extend([row['comptsValoresImpostos'][0][k] for k in attributes_required_comptsvals])
            try:
                G5(*args, compt=self.compt)
            except Exception as e:
                print(args)
                raise e
            else:
                row['nf_saidas'] = 'OK'
                self.compts_repository.update_from_dictionary(row.to_dict())
                self._run_update_cloud(row)

    def call_pgdas_declaracao(self):
        # df = self.aps.client_compts_df
        # df = self.compts_repository.get_interface_df()
        df = self.compts_repository.query_data_by_routine_in_compt('todas')
        attributes_required = ['razao_social', 'cnpj', 'cpf',
                               'codigo_simples', 'ha_procuracao_ecac']
        merged_df_cod_acesso = df.loc[df['ha_procuracao_ecac'] == 'não', :]
        merged_df_proc_ecac = df.loc[(df['ha_procuracao_ecac'] == 'sim') & (df['codigo_simples'] == ''), :]
        merged_df = pd.concat([merged_df_cod_acesso, merged_df_proc_ecac], ignore_index=True)

        # ecac_driver = default_qrcode_driver('C:\\Temp')
        ecac_driver = pgdas_driver()
        for e, row in merged_df.iterrows():
            imposto = row['comptsValoresImpostos'][0]['imposto_a_calcular']
            if not row['pode_declarar']:
                continue
            if imposto == 'LP':
                continue

            else:
                valor_total, all_valores = self._generate_all_valores(row['comptsValoresImpostos'])
                row_required = row[attributes_required]
                args = row_required.to_list()
                args.insert(-1, valor_total)
                try:
                    args[-1] = ''
                    if row['ha_procuracao_ecac'] == 'sim' and str(row['codigo_simples']) == '':
                        PgdasDeclaracao(*args, compt=self.compt, all_valores=all_valores,
                                        driver=ecac_driver)
                    else:
                        PgdasDeclaracao(*args, compt=self.compt, all_valores=all_valores)

                except Exception as e:
                    print(f'Failed: {row["razao_social"]}')
                else:
                    row['declarado'] = True
                    # self.valores_repository.dba.query(f'SELECT * FROM OE_COMPTS_VALORES_IMPOSTOS WHERE ID={row["comptsValoresImpostos"][0]["id"]}')
                    self.compts_repository.update_from_dictionary(row.to_dict())

                    self._run_update_cloud(row, shall_update_valores=True)

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
                               'declarado']

        # required_df = df.loc[:, attributes_required]  # type: pd.DataFrame
        for e, row in df.iterrows():
            valor_total, all_valores = self._generate_all_valores(row['comptsValoresImpostos'])
            imposto_a_calcular = row['comptsValoresImpostos'][0]['imposto_a_calcular']

            row_required = row[attributes_required]
            envio = row['envio']

            if not envio and row['declarado']:
                PgDasmailSender(*row_required, valor_total, imposto_a_calcular, envio, compt=self.compt,
                                venc_das=row['venc_das'] or self.aps.get_venc_das(),
                                email=row['email'])
                row['envio'] = True
                self.compts_repository.update_from_dictionary(row.to_dict())
                self._run_update_cloud(row)

    def run_oesk_project_excel(self):

        subprocess.Popen("O:\\HACKING\\MY_PROJECTS\\oesk\\backend\\utilities\\scripts\\run_react_project.bat")
