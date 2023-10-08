import pandas as pd

from backend.utilities.db import DbAccessManager
from backend.models import OrmTables
from backend.utilities.compt_utils import get_compt, compt_to_date_obj, calc_date_compt_offset, ate_atual_compt, \
    get_all_valores
from backend.utilities.helpers import modify_dataframe_at, sort_dataframe
import sqlalchemy as sql
from typing import Union, List, Tuple
from backend.repository.utils import RepositoryUtils

# OrmTables.MainEmpresas
# OrmTables.ClientsCompts

main_empresas, clients_compts = OrmTables.get_classes().values()


class MainEmpresasRepository(RepositoryUtils):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.MainEmpresas
        super().__init__(self.orm, self.Session)

    # override
    def get_as_orm(self, row) -> OrmTables.MainEmpresas:
        kwargs = {
            'id': row.id,
        }
        return super().get_as_orm(**kwargs)


class ClientComptsRepository(RepositoryUtils):
    def __init__(self, compt: str):
        self.main_compt = compt_to_date_obj(compt)
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.ClientsCompts
        super().__init__(self.orm, self.Session)
        self.main_empresas = OrmTables.MainEmpresas
        self._add_new_compt()

    # override
    def get_as_orm(self, row) -> OrmTables.ClientsCompts:
        kwargs = {
            'id': row.id,
            'main_empresa_id': row.main_empresa_id
        }
        return super().get_as_orm(**kwargs)

    # Queries
    def _query_all_data_in_compt(self, is_authorized=False, must_have_status_ativo=True, to_df=True, another_compt=None) -> Union[
        pd.DataFrame, List[sql.orm.Query]]:
        """Get a DataFrame or a list of ORM queries by joining all registered fields.

        :param is_authorized: Filter by 'pode_declarar' in the ORM.
        :param must_have_status_ativo: Filter by 'status_ativo'. Defaults to True.
        :param to_df: If True, return a DataFrame; if False, return a list of ORM queries.
        :param another_compt: if you need to query another specific compt
        :return: Either a DataFrame or a list of ORM queries.
        """
        with self.Session() as session:
            query = session.query(self.orm, self.main_empresas).filter_by(compt=another_compt or self.main_compt)
            if is_authorized:
                query = query.filter_by(pode_declarar=True)
            query = query.join(self.main_empresas, self.orm.main_empresa_id == self.main_empresas.id)
            if must_have_status_ativo:
                query = query.filter_by(status_ativo=True)
            if to_df:
                return self.dba.query_to_dataframe(query)
            else:
                return query.all()

    def _get_ordered_by_imposto_a_calcular(self, sorting_list: list = None, allowing_list: list = None,
                                           allow_lucro_presumido=False,
                                           allow_only_authorized=False) -> pd.DataFrame:
        """
        Retrieve and sort a DataFrame of financial data by 'imposto_a_calcular' column based on a custom order list.

        :param sorting_list: A list specifying the desired sorting order for 'imposto_a_calcular' values.
                           if None, calls default_order
        :param allowing_list: A list containing the 'imposto_a_calcular' that should be in data
        :param allow_lucro_presumido: If False, filter out rows with 'imposto_a_calcular' value 'LP'
                                      (Lucro Presumido). Default is False.
        :param allow_only_authorized: If True, filter the DataFrame to include only authorized data.
                                      Default is True.
        :return: A sorted DataFrame containing financial data with 'imposto_a_calcular' column values
                 ordered according to the provided order list.
'        """
        default_order = ["SEM_MOV", "ISS", "ICMS"]
        main_df = self._query_all_data_in_compt(is_authorized=allow_only_authorized)
        sorted_df = sort_dataframe(main_df, sorting_list or default_order, 'imposto_a_calcular')

        if not allow_lucro_presumido and allowing_list is not None and 'LP' not in allowing_list:
            sorted_df = sorted_df.loc[sorted_df['imposto_a_calcular'] != 'LP']

        if allowing_list:
            sorted_df = sorted_df.loc[sorted_df['imposto_a_calcular'].isin(allowing_list)]

        return sorted_df

    def get_interface_df(self, allowing_impostos_list=None) -> pd.DataFrame:
        df = self._get_ordered_by_imposto_a_calcular(sorting_list=['ISS', 'ICMS', 'SEM_MOV', 'LP'],
                                                     allowing_list=allowing_impostos_list)
        return df

    def get_g5_df(self) -> Tuple[list, pd.DataFrame]:
        df = self._get_ordered_by_imposto_a_calcular(sorting_list=['ISS'])
        df = self._get_ordered_by_imposto_a_calcular(allowing_list=['ISS'])

        # TODO: separar G5 por ISS e ICMS
        print(df)

    def get_df_to_email(self) -> pd.DataFrame:
        df = self._get_ordered_by_imposto_a_calcular(allow_only_authorized=True)
        df = df.loc[df['envio'].isin(False)]
        return df

    # Updates...
    def update_from_object(self, orm: OrmTables.MainEmpresas):
        """Overriden"""
        super().update_from_object(orm)

    # add new compt
    def _add_new_compt(self) -> None:
        with self.Session() as session:
            # check if the row already exists
            row_exists = session.query(self.orm).filter(
                self.orm.compt == self.main_compt).first()
            if not row_exists:
                print("Init new compt: ", self.main_compt, '-------')
                # create new rows with incremented date

                for row in self._query_all_data_in_compt(to_df=False, another_compt=row_exists.compt):
                    _envio = True if str(
                        row.imposto_a_calcular) == 'LP' else False
                    # TODO make it below work
                    # _declarado = True if str(
                    #     row.imposto_a_calcular) == 'LP' and '//' not in row.ginfess_cod else False
                    _declarado = False
                    def get_status_imports_g5(
                            campo: str): return campo if campo.upper() != 'OK' else ''

                    new_row = self.orm(
                        main_empresa_id=row.main_empresa_id,
                        declarado=_declarado,
                        nf_saidas=get_status_imports_g5(row.nf_saidas),
                        nf_entradas=get_status_imports_g5(row.nf_entradas),
                        sem_retencao=0.00,
                        com_retencao=0.00,
                        valor_total=0.00,
                        anexo=row.anexo,
                        imposto_a_calcular=row.imposto_a_calcular,
                        possui_das_pendentes=False,
                        compt=self.main_compt
                        ,
                        envio=_envio,
                        pode_declarar=False  # set to False
                    )
                    session.add(new_row)
                session.commit()

    def __add_new_client(self, empresa_id, imposto_a_calcular):
        # Vou utilizar anexo sugerido...
        if imposto_a_calcular == 'ICMS':
            anexo_sugerido = 'I'
        elif imposto_a_calcular == 'ISS':
            anexo_sugerido = 'III'
        else:
            anexo_sugerido = ''

        with self.Session() as session:
            exists = session.query(self.orm).filter_by(
                compt=self.main_compt, main_empresa_id=empresa_id).first()

            if not exists:
                _envio = True if str(
                    imposto_a_calcular) == 'LP' else False
                _declarado = True if str(
                    imposto_a_calcular) == 'LP' else False
                new_row = self.orm(
                    main_empresa_id=empresa_id,
                    declarado=_declarado,
                    nf_saidas='',
                    nf_entradas='',
                    sem_retencao=0.00,
                    com_retencao=0.00,
                    valor_total=0.00,
                    anexo=anexo_sugerido,
                    imposto_a_calcular=imposto_a_calcular,
                    possui_das_pendentes=False,
                    compt=self.main_compt,
                    envio=_envio,
                    pode_declarar=False  # set to False
                )
                session.add(new_row)
                session.commit()
                return True
            return False


if __name__ == '__main__':
    cc = ClientComptsRepository(compt='08-2023')
    me = MainEmpresasRepository()
    # df = cc.query(id=2)
    cc.get_g5_df()
