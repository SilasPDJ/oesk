import pandas as pd

from utilities.db import DbAccessManager
from models import OrmTables
from utilities.compt_utils import get_compt, compt_to_date_obj, calc_date_compt_offset, ate_atual_compt, get_all_valores
import sqlalchemy as sql
from typing import Union, List

# OrmTables.MainEmpresas
# OrmTables.ClientsCompts

main_empresas, clients_compts = OrmTables.get_classes().values()


class CustomMethods:
    def __init__(self, orm, session):
        self.orm = orm
        self.Session = session

    @property
    def _orm_columns(self) -> list:
        return [column.name for column in self.orm.__table__.columns]

    @staticmethod
    def sort_dataframe(main_df: pd.DataFrame, order_list: list, sorting_key: str) -> pd.DataFrame:
        """Sorts a DataFrame based on a specified order list and a sorting key."""

        main_df['sorting_key'] = main_df[sorting_key].apply(
            lambda x: order_list.index(x) if x in order_list else len(order_list))
        sorted_df = main_df.sort_values(by='sorting_key').drop(columns='sorting_key')
        return sorted_df

    # update methods
    def update_from_dataframe(self, df: pd.DataFrame):
        """Updates a database's table based on a dataframe, (allows multiple rows)"""
        with self.Session() as session:
            for row in df.itertuples(index=False):
                # preventing data from joins
                data_to_orm = {column: getattr(row, column) for column in self._orm_columns}

                session.merge(self.orm(**data_to_orm))
                # session.merge(self.orm(**row._asdict()))
            session.commit()

    def update_from_dictionary(self, dictionary: dict):
        """update a database's table based on a dictionary, (once per time)"""
        with self.Session() as session:
            # preventing data from joins
            dict_to_orm = {key: dictionary[key] for key in self._orm_columns if key in dictionary}

            session.merge(self.orm(**dict_to_orm))
            # session.merge(self.orm(**dictionary))
            session.commit()


class MainEmpresasRepository(CustomMethods):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.MainEmpresas
        super().__init__(self.orm, self.Session)


class ClientComptsRepository(CustomMethods):
    def __init__(self, compt: str):
        self.main_compt = compt_to_date_obj(compt)
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.ClientsCompts
        super().__init__(self.orm, self.Session)
        self.main_empresas = OrmTables.MainEmpresas

    # Queries
    def get_full_data_in_compt(self, is_authorized=False, must_have_status_ativo=True, to_df=True) -> Union[
        pd.DataFrame, List[sql]]:
        """Get a DataFrame or a list of ORM queries by joining all registered fields.

        :param is_authorized: Filter by 'pode_declarar' in the ORM.
        :param must_have_status_ativo: Filter by 'status_ativo'. Defaults to True.
        :param to_df: If True, return a DataFrame; if False, return a list of ORM queries.
        :return: Either a DataFrame or a list of ORM queries.
        """
        with self.Session() as session:
            query = session.query(self.orm, self.main_empresas).filter_by(compt=self.main_compt)
            if is_authorized:
                query = query.filter_by(pode_declarar=True)
            query = query.join(self.main_empresas, self.orm.main_empresa_id == self.main_empresas.id)
            if must_have_status_ativo:
                query = query.filter_by(status_ativo=True)
            if to_df:
                return self.dba.query_to_dataframe(query)
            else:
                return query.all()

    def get_ordered_by_imposto_a_calcular(self, order_list: list = None, allow_lucro_presumido=False,
                                          allow_only_authorized=True) -> pd.DataFrame:
        """
        Retrieve and sort a DataFrame of financial data by 'imposto_a_calcular' column based on a custom order list.

        :param order_list: A list specifying the desired sorting order for 'imposto_a_calcular' values.
                           if None, calls default_order

        :param allow_lucro_presumido: If False, filter out rows with 'imposto_a_calcular' value 'LP'
                                      (Lucro Presumido). Default is False.
        :param allow_only_authorized: If True, filter the DataFrame to include only authorized data.
                                      Default is True.
        :return: A sorted DataFrame containing financial data with 'imposto_a_calcular' column values
                 ordered according to the provided order list.
'        """
        default_order = ["SEM_MOV", "ISS", "ICMS"]
        main_df = self.get_full_data_in_compt(is_authorized=allow_only_authorized)
        sorted_df = self.sort_dataframe(main_df, order_list or default_order, 'imposto_a_calcular')

        if not allow_lucro_presumido:
            sorted_df = sorted_df.loc[sorted_df['imposto_a_calcular'] != 'LP']

        return sorted_df

    # Updates...


if __name__ == '__main__':
    cc = ClientComptsRepository(compt='08-2023')
    me = MainEmpresasRepository()
    # df = cc.query(id=2)
    df = cc.get_full_data_in_compt()

    df = cc.get_ordered_by_imposto_a_calcular(['ISS', 'ICMS', 'SEM_MOV'])

    with cc.Session() as session:
        dale = session.query(me.orm).filter_by(id=1)
        df = cc.get_ordered_by_imposto_a_calcular()
        df = df.loc[df['main_empresa_id'] == 2]
        # dale = session.query(cc.orm).filter_by(id=1726)

        # df = me.dba.query_to_dataframe(dale)
        # df['razao_social'][0] = "Agathadiesel Mecanica e Manutencao de Veiculos LTDA removeZ"
        df['valor_total'] = 12
        # me.update_from_dataframe(df)
        cc.update_from_dataframe(df)
        for d in dale:
            df = me.dba.query_to_dataframe(d)
            print(d)
            # d.razao_social = "ADEILTON Teste"
        session.commit()
    print(df)

    print(df)
