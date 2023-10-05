import pandas as pd
import tkinter as tk
import os
import sys

# backend = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', "backend"))
# sys.path.insert(1, backend)


class AppSettings:
    current_client_index = 0

    """App Settings"""

    "campos copiaveis"
    copiable_fields = [
        'razao_social', 'cnpj', 'valor_total', 'codigo_simples', 'email',
        'sem_retencao', 'com_retencao', 'cpf', 'anexo',
        'gissonline', 'giss_login', 'ginfess_cod', 'ginfess_link',
        'possui_das_pendentes', 'status_ativo', 'main_empresa_id']

    def map_ids_with_col_to_dict(self, keys_field, values_field) -> dict:
        """
        :param values_field:
        :return:
        """
        df = self.client_compts_df
        return {k: v for k, v in zip(df[keys_field], df[values_field])}

    @property
    def compt(self):
        return self._compt

    @compt.setter
    def compt(self, value):
        self._compt = value

    @property
    def client_compts_df(self) -> pd.DataFrame:
        return self._client_compts_df

    @client_compts_df.setter
    def client_compts_df(self, value):
        self._client_compts_df = value

    @property
    def allowed_clients(self) -> tk.StringVar:
        return self._allowed_clients

    @allowed_clients.setter
    def allowed_clients(self, col):
        _clients_permited = self.client_compts_df[col].to_list()
        self._allowed_clients = tk.StringVar(value=_clients_permited)

    @property
    def current_client_index(self):
        return self._current_client

    @current_client_index.setter
    def current_client_index(self, value):
        self._current_client = value
