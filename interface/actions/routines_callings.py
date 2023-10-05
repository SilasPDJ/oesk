import os
import sys
import clipboard
import subprocess

import pandas as pd

from backend.repository import MainEmpresasRepository, ClientComptsRepository
from interface.settings import AppSettings


class RoutinesCallings:
    def __init__(self, app_settings: AppSettings):
        # composição... recebendo self
        self.aps = app_settings

        self.compts_repository = ClientComptsRepository(self.aps.compt)
        # Abaixo não funciona pq oobjeto ta sendo atualizado dentro da classe
        # client_compts_df = self.aps.client_compts_df

    def call_ginfess(self):
        df = self.aps.client_compts_df

    def call_g5(self):
        df = self.aps.client_compts_df

    def call_simples_nacional(self):
        df = self.aps.client_compts_df

    def call_gias(self):
        df = self.aps.client_compts_df

    def call_giss(self):
        df = self.aps.client_compts_df

    def call_func_v3(self):
        df = self.aps.client_compts_df

    def call_send_pgdas_email(self, a):
        df = self.aps.client_compts_df
