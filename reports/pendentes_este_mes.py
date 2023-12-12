import os
from typing import Union

from repository import ClientComptsRepository
from utilities.compt_utils import ate_atual_compt, get_compt, get_compt_as_date
import pandas as pd
from utilities.default.sets import FileOperations


def get_filepath(filename) -> Union[bytes, str]:
    def get_ano():
        compt_date = get_compt_as_date()
        return compt_date.year

    folder = file_operations.files_pathit('RELATORIOS', '', ano=get_ano())
    return os.path.join(folder, filename)


def gerar_report_outros_zerados(meses: int, relatorio_filename_preffix: str):
    dfs = []
    for compt in ate_atual_compt(get_compt(), get_compt(meses)):
        df = ClientComptsRepository(compt)
        dfs.append(df._query_all_data_in_compt())

    df = pd.concat(dfs)

    zerados = df.loc[
        (df['valor_total'] == 0) &
        (~df['imposto_a_calcular'].isin(['SEM_MOV', 'LP']))
        ]

    # TODO

    relatorio = df[
        ['compt', 'razao_social', 'cnpj', 'valor_total', 'imposto_a_calcular', 'status_ativo', 'email']]

    relatorio = relatorio.sort_values(by=['cnpj', 'compt'])
    relatorio.to_excel(get_filepath(relatorio_filename_preffix + 'PENDENTES.xlsx'), index=False)
    print(df)


if __name__ == '__main__':
    file_operations = FileOperations()

    gerar_report_outros_zerados(12, 12)
