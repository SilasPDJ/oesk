import pandas as pd
import tkinter as tk


class AppSettings:
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
    def current_client(self):
        return self._current_client

    @current_client.setter
    def current_client(self, value):
        self._current_client = value
