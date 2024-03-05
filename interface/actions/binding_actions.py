import os
import sys
import clipboard
import subprocess

import pandas as pd

from backend.utilities.default.sets import FileOperations
from backend.repository import ClientComptsRepository
from interface.settings import AppSettings


class BindingActions:
    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings
        # self.compts_repository = ClientComptsRepository(self.aps.compt)

        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def create_new_isntance(self):
        # os.execl(sys.executable, sys.executable, *sys.argv)
        subprocess.Popen([sys.executable, sys.argv[0]], shell=False)

    def get_selected_client_df(self) -> pd.DataFrame:
        df = self.aps.client_compts_df
        current_client_index = self.aps.current_client_index
        return df.iloc[current_client_index, :]

    def _obeter_pasta_cliente(self, pasta_client_label: str):
        selected_client = self.get_selected_client_df()
        pasta_client = selected_client[pasta_client_label]

        folder = FileOperations.files_pathit(pasta_client, self.aps.compt)
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def f1_abre_pasta(self, pasta_client_label):
        folder = self._obeter_pasta_cliente(pasta_client_label)
        subprocess.Popen(f'explorer "{folder}"')

    def f2_copy_path(self, pasta_client_label):
        folder = self._obeter_pasta_cliente(pasta_client_label)
        clipboard.copy(folder)
        # selected_client = self.get_selected_client_df()

    def copy_data_to_clipboard(self, field: str):
        selected_client = self.get_selected_client_df()

        searching_by_field_result = selected_client[field]
        clipboard.copy(searching_by_field_result)
        return searching_by_field_result
