import os

from backend.pgdas_fiscal_oesk.giss_online_pt12 import GissGui

import pandas as pd

from utilities.compt_utils import get_compt

thispath = os.path.dirname(__file__)
folder = os.path.join(thispath,
                      'backend', 'pgdas_fiscal_oesk\\data_clients_files')
file = os.path.join(folder, 'gissonline_csv.csv')
df = pd.read_csv(file)

for data in df.itertuples():
    client_name = getattr(data, 'name')
    client_login = getattr(data, 'login')
    client_pswd = getattr(data, 'pswd')

    GissGui([client_name, None, client_login], compt=get_compt(), headless=False, pswd=client_pswd)
