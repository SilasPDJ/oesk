import os
import clipboard
import subprocess

def abre_pasta(self, event=None):
    folder = InitialSetting.files_pathit(self.selected_client.get(), COMPT)
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

def call_simples_nacional():
    print('sn')
def call_gias():
    print('gias')
def call_ginfess():
    pass

def call_giss():
    pass

def call_g5():
    pass
def call_func_v3(a):
    print(a)

def call_send_pgdas_email():
    pass
    print('pgdas email bt')

