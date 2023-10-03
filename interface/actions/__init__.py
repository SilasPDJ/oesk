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
        self.clients_permited = self.aps.allowed_clients
        self.client_compts_df = self.aps.client_compts_df

    def abre_pasta(self, event=None):
        folder = FileOperations.files_pathit(self.aps.current_client, self.aps.compt)
        if not os.path.exists(folder):
            os.makedirs(folder)
        subprocess.Popen(f'explorer "{folder}"')
        clipboard.copy(folder)

    def copy_data_to_clipboard(self, event=None):
        campo = event.widget.get() if event else ""
        if campo == '':
            campo = "cnpj"
        found_object = self.EMPRESAS_ORM_OPERATIONS.filter_by_razao_social(
            self.selected_client.get())
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

