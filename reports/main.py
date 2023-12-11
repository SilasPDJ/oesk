import os
from typing import Union

from repository import ClientComptsRepository
from utilities.compt_utils import ate_atual_compt, get_compt, get_compt_as_date
import pandas as pd
from utilities.default.sets import FileOperations

if __name__ == '__main__':
    def get_filepath(filename) -> Union[bytes, str]:
        def get_ano():
            compt_date = get_compt_as_date()
            return compt_date.year

        folder = file_operations.files_pathit('RELATORIOS', '', ano=get_ano())
        return os.path.join(folder, filename)


    file_operations = FileOperations()
    dfs = []
    for compt in ate_atual_compt(get_compt(), get_compt(4)):
        df = ClientComptsRepository(compt)
        dfs.append(df._query_all_data_in_compt())

    df = pd.concat(dfs)

    zerados = df.loc[
        (df['valor_total'] == 0) &
        (~df['imposto_a_calcular'].isin(['SEM_MOV', 'LP']))
        ]

    zerados_duplicados_mais_de_2 = zerados[zerados.groupby('id_1')['id_1'].transform('count') > 2]
    zerados_duplicados_mais_de_2 = zerados_duplicados_mais_de_2.sort_values(by='id_1')

    relatorio = zerados_duplicados_mais_de_2[
        ['compt', 'razao_social', 'cnpj', 'valor_total', 'imposto_a_calcular', 'status_ativo', 'email']]

    relatorio = relatorio.sort_values(by=['cnpj', 'compt'])
    relatorio.to_excel(get_filepath('RELATORIO_ZERADOS_COM_INCIDENCIA.xlsx'))
    print(df)
