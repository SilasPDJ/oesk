from utilities.default import *
from pyperclip import paste
# from default.webdriver_utilities import *
from win11toast import toast
from pgdas_fiscal_oesk.contimatic import *

"""
from LE_NF_CANCELADAS_cor import main as nf_canceled
import ATIVA_EMPRESA
import PROGRAMA_REQUIRED
import NEEDED_PANDAS
from datetime import datetime
import os
"""

# um por um?
# vai p/ NEEDED_PANDAS

# ctrl_shift+M


class JR(Contimatic):

    def __init__(self, *args, compt):

        __r_social, __cnpj, = args
        __client = __r_social

        self.compt_used = compt
        self.client_path = self.files_pathit(__client, self.compt_used)
        super().__init__(self.client_path)

        can_be_declared = self.walget_searpath(
            "APUR_ICMS", self.client_path, 2)
        # can_be_declared += self.walget_searpath(
        #     "LIVRO_ENTRADA", self.client_path, 2)
        can_be_declared += self.walget_searpath(
            "LIVRO_SAIDA", self.client_path, 2)
        print(
            "\033[1;31m Estou procurando declarações. EXCLUIR CASO RETIFICAR\033[m")

        if can_be_declared and not self.walget_searpath("PGDASD-DECLARACAO", self.client_path, 2):
            registronta = self.registronta()
            # input(registronta)
            print(__client)
            self.abre_ativa_programa('JR ')

            all_xls_inside = self.files_get_anexos_v4(
                self.client_path, file_type='xlsx')
            relacao_notas = all_xls_inside[0] if len(
                all_xls_inside) == 1 else IndexError()
            self.activating_client(self.formatar_cnpj(__cnpj))
            pygui.getActiveWindow().maximize()
            # Agora vai ser por cnpj...
            self.start_walk_menu()
            foritab(2, 'right')
            foritab(7, 'down')
            pygui.hotkey('right')
            foritab(7, 'down')
            pygui.hotkey('enter')

            # access ISS lançamento
            toast("Pressione F9 para ativar o próximo cliente", duration="medium")
            press_key_b4('f9')
