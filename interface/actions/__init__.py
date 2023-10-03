import os
import clipboard
import subprocess

import pandas as pd

from utilities.default.sets import FileOperations
from repository import MainEmpresasRepository, ClientComptsRepository

class Actions:
    def __init__(self, app_instance):
        # composição...
        self.app = app_instance
        self.compts_repository = ClientComptsRepository(self.app.compt)
        self.clients_permited = self.app.allowed_clients   # type: list
        self.client_compts_df = self.app.client_compts_df  # type: pd.DataFrame

    def abre_pasta(self, event=None):
        folder = FileOperations.files_pathit(self.app.current_client, self.app.compt)
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

