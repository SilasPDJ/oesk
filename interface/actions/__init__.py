import os
import clipboard
import subprocess

import pandas as pd

from utilities.default.sets import FileOperations
from repository import MainEmpresasRepository, ClientComptsRepository
from interface.settings import AppSettings


class Actions:
    def __init__(self, app_settings: AppSettings):
        # composição...
        self.aps = app_settings
        self.compts_repository = ClientComptsRepository(self.aps.compt)

        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def get_selected_client_df(self) -> pd.DataFrame:
        df = self.aps.client_compts_df
        current_client_index = self.aps.current_client_index
        return df.iloc[current_client_index, :]

    def abre_pasta(self, pasta_client_label):
        selected_client = self.get_selected_client_df()

        pasta_client = selected_client[pasta_client_label]

        folder = FileOperations.files_pathit(pasta_client, self.aps.compt)
        if not os.path.exists(folder):
            os.makedirs(folder)
        subprocess.Popen(f'explorer "{folder}"')
        clipboard.copy(folder)

    def copy_data_to_clipboard(self, field: str):
        # TODO: fix quando seleciona outro field no interface/main.py
        selected_client = self.get_selected_client_df()

        searching_by_field_result = selected_client[field]
        clipboard.copy(searching_by_field_result)
        return searching_by_field_result

    def call_simples_nacional(self):
        print('sn')

    def call_gias(self):
        print('gias')

    def call_ginfess(self):
        pass

    def call_giss(self):
        pass

    def call_g5(self):
        pass

    def call_func_v3(selfa):
        print(a)

    def call_send_pgdas_email(self, a):
        pass
        print('pgdas email bt')
