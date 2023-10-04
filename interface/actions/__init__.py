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


    def abre_pasta(self, event=None):
        current_client = self.aps.current_client
        folder = FileOperations.files_pathit(current_client, self.aps.compt)
        if not os.path.exists(folder):
            os.makedirs(folder)
        subprocess.Popen(f'explorer "{folder}"')
        clipboard.copy(folder)

    def copy_data_to_clipboard(self, field: str):
        cliente = self.aps.current_client

        # ids = self.aps.allowed_ids
        my_dict = self.aps.map_ids_with_col_to_dict(field)
        ids_to_filter = list(my_dict.keys())

        found_objects = self.aps.client_compts_df.query('id_1 in @ids_to_filter')
        returned = getattr(found_object, campo)
        clipboard.copy(returned)
        return returned

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

    def call_send_pgdas_email(self,a):
        pass
        print('pgdas email bt')

