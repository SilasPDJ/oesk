import pandas as pd
import tkinter as tk
from dotenv import load_dotenv


class AppSettings:
    current_client_index = 0

    """App Settings"""

    "campos copiaveis"
    copiable_fields = [
        'razao_social', 'cnpj', 'valor_total', 'codigo_simples', 'email',
        'sem_retencao', 'com_retencao', 'cpf', 'anexo',
        'gissonline', 'giss_login', 'ginfess_cod', 'ginfess_link',
        'venc_das', 'status_ativo', 'main_empresa_id']
    
    main_df_col = None
    load_dotenv()

    def map_ids_within_col_to_dict(self, keys_field: list, values_field: list) -> dict:
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
    def venc_das(self):
        return self._venc_das

    @venc_das.setter
    def venc_das(self, venc_das):
        self._venc_das = tk.StringVar(value=venc_das)

    @property
    def client_compts_df(self) -> pd.DataFrame:
        return self._client_compts_df

    def get_venc_das(self):
        return self.venc_das.get()

    @client_compts_df.setter
    def client_compts_df(self, value):
        self.main_df_col = value
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

    @property
    def allowed_dict_ids(self) -> dict:
        _ids_permited = self.client_compts_df['id'].to_list()
        return {k: v for k, v in zip(_ids_permited, self.allowed_clients.get())}
