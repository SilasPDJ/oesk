import pandas as pd

from utilities.db import DbAccessManager
from models import OrmTables
from utilities.compt_utils import get_compt, compt_to_date_obj, calc_date_compt_offset, ate_atual_compt, get_all_valores
import sqlalchemy as sql

# OrmTables.MainEmpresas
# OrmTables.ClientsCompts

main_empresas, clients_compts = OrmTables.get_classes().values()


class Default:

    def get_ordered_by(self, orm, order_list, key):
        _str_col = key




class MainEmpresasRepository:
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.MainEmpresas


class ClientComptsRepository:
    def __init__(self, compt: str):
        self.main_compt = compt_to_date_obj(compt)
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.ClientsCompts
        self.main_empresas = OrmTables.MainEmpresas

    def get_full_df_in_compt(self, is_authorized=False, must_have_status_ativo=True) -> pd.DataFrame:
        """ Get df joining all register fields
        :param is_authorized: pode_declarar in orm
        :param must_have_status_ativo: filter with status_ativo. Defaults to True
        :return:
        """
        with self.Session() as session:
            query = session.query(self.orm, self.main_empresas).filter_by(compt=self.main_compt)
            if is_authorized:
                query = query.filter_by(pode_declarar=True)
            query = query.join(self.main_empresas, self.orm.main_empresa_id == self.main_empresas.id)
            if must_have_status_ativo:
                query = query.filter_by(status_ativo=True)

            # for q in query:
            #     print(q)
            return self.dba.query_to_dataframe(query)

    def get_ordered_by_imposto_a_calcular(self, order_list: list, allow_lucro_presumido=False,
                                          allow_only_authorized=True) -> pd.DataFrame:
        """
        Retrieve and sort a DataFrame of financial data by 'imposto_a_calcular' column based on a custom order list.

        :param order_list: A list specifying the desired sorting order for 'imposto_a_calcular' values.
        :type order_list: list
        :param allow_lucro_presumido: If False, filter out rows with 'imposto_a_calcular' value 'LP'
                                      (Lucro Presumido). Default is False.
        :type allow_lucro_presumido: bool, optional
        :param allow_only_authorized: If True, filter the DataFrame to include only authorized data.
                                      Default is True.
        :type allow_only_authorized: bool, optional

        :return: A sorted DataFrame containing financial data with 'imposto_a_calcular' column values
                 ordered according to the provided order list.
'        """
        main_df = self.get_full_df_in_compt(is_authorized=allow_only_authorized)

        # Create a custom sorting key based on the order_list
        _str_col = 'imposto_a_calcular'
        main_df['sorting_key'] = main_df[_str_col].apply(
            lambda x: order_list.index(x) if x in order_list else len(order_list))

        # Sort the DataFrame by the custom sorting key and drop the sorting_key column
        sorted_df = main_df.sort_values(by='sorting_key').drop(columns='sorting_key')

        if not allow_lucro_presumido:
            sorted_df = sorted_df.loc[sorted_df[_str_col] != 'LP']

        return sorted_df


if __name__ == '__main__':
    cc = ClientComptsRepository(compt='01-2023')
    # df = cc.query(id=2)
    df = cc.get_full_df_in_compt()

    df = cc.get_ordered_by_imposto_a_calcular(['ISS', 'ICMS', 'SEM_MOV'])
    print(df)

    print(df)
