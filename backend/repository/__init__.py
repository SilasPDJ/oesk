import pandas as pd
from typing import Union, List, Tuple

from backend.utilities.db import DbAccessManager
from backend.models import OrmTables
from backend.utilities.compt_utils import get_compt, compt_to_date_obj, calc_date_compt_offset, ate_atual_compt, \
    get_all_valores, get_next_venc_das
from backend.repository.utils import RepositoryUtils
from backend.utilities.helpers import modify_dataframe_at, sort_dataframe
import sqlalchemy as sql


# OrmTables.MainEmpresas
# OrmTables.ClientsCompts


class OeEmpresasRepository(RepositoryUtils):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.OEEmpresas
        super().__init__(self.orm, self.Session)

    def query_empresas(self, cnpj=None):
        with self.Session() as session:
            query = session.query(self.orm)
            if cnpj is not None:
                query.filter_by(cnpj=cnpj)

            return self.dba.query_to_dataframe(query)


class OeGiasRepository(RepositoryUtils):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.OEGias
        super().__init__(self.orm, self.Session)


class OeServicosRepository(RepositoryUtils):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.OEServicos
        super().__init__(self.orm, self.Session)


class OeICMSRepository(RepositoryUtils):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.OEEmpresasICMS_SemMov
        super().__init__(self.orm, self.Session)


class OeComptsValoresImpostosRepository(RepositoryUtils):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.ComptsValoresImpostos
        super().__init__(self.orm, self.Session)


class OeClientComptsRepository(RepositoryUtils):
    def __init__(self, compt: str):
        self.main_compt = compt_to_date_obj(compt)
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.ClientsCompts
        super().__init__(self.orm, self.Session)
        # self.main_empresas = OrmTables.MainEmpresas
        self.empresas = OrmTables.OEEmpresas
        self.empresas_gias = OrmTables.OEGias
        self.empresas_iss = OrmTables.OEServicos
        self.empresas_icms = OrmTables.OEEmpresasICMS_SemMov

        self.valores_impostos = OrmTables.ComptsValoresImpostos
        self._add_new_compt()
        # TODO add new compt

    # override
    def get_as_orm(self, row) -> OrmTables.ClientsCompts:
        kwargs = {
            'id': row.id,
            # 'main_empresa_id': row.main_empresa_id
            'main_empresa_id': row.empresa_id
        }
        return super().get_as_orm(**kwargs)

    # Queries

    def query_data_by_routine_in_compt(self, tipo_empresa_rotina: str, must_be_authorized=False,
                                       must_have_status_ativo=True,
                                       to_df=True,
                                       ) -> Union[pd.DataFrame, List[sql.orm.Query]]:
        """Get a DataFrame or a list of ORM queries by joining all registered fields based on its routine and compt
        :param tipo_empresa_rotina: interface -> join valores_df (can have duplicated)
        :param must_be_authorized: Filter by 'pode_declarar'. Defaults to False
        :param must_have_status_ativo: Filter by 'status_ativo'. Defaults to True.
        :param to_df: If True, return a DataFrame; if False, return a list of ORM queries.
        :return: Either a DataFrame or a list of ORM queries.
        """
        tipo_empresa_rotina = tipo_empresa_rotina.lower().strip()
        assert tipo_empresa_rotina in ['sem_mov', 'iss', 'icms', 'gias', 'outros',
                                       'todas', 'interface'], 'tipo_empresa_rotina inválido'

        with self.Session() as session:
            # tipo rotina:
            if tipo_empresa_rotina == 'gias':
                query = session.query(self.orm, self.empresas, self.empresas_gias).filter_by(compt=self.main_compt)
                query = query.join(self.empresas_gias, self.orm.empresa_id == self.empresas_gias.empresa_id)
                # -- valores depois dos dados
                query = query.join(self.empresas, self.orm.empresa_id == self.empresas.id)
            elif tipo_empresa_rotina == 'iss':
                query = session.query(self.orm, self.empresas, self.empresas_iss).filter_by(compt=self.main_compt)
                query = query.join(self.empresas_iss, self.orm.empresa_id == self.empresas_iss.empresa_id)
                # -- valores depois dos dados
                query = query.join(self.empresas, self.orm.empresa_id == self.empresas.id)
            elif tipo_empresa_rotina == 'icms' or tipo_empresa_rotina == 'sem_mov':
                query = session.query(self.orm, self.empresas_icms)
                # no need main from empresas, 'cause empresas_icms is already based on it
                query = query.join(self.empresas_icms, self.orm.empresa_id == self.empresas_icms.id)
            elif tipo_empresa_rotina == 'todas' or tipo_empresa_rotina == 'interface':
                query = session.query(self.orm, self.empresas).filter_by(compt=self.main_compt)
                query = query.join(self.empresas, self.orm.empresa_id == self.empresas.id)
            else:
                raise ValueError("Surgiram outros...")

            if must_be_authorized:
                query = query.filter_by(pode_declarar=True)
            if must_have_status_ativo:
                query = query.filter_by(status_ativo=True)

            # query valores
            main_df = self.dba.query_to_dataframe(query)
            valores_df = self.query_valores_df()

            if tipo_empresa_rotina == 'interface':
                return pd.merge(main_df, valores_df, how='left', left_on='id', right_on='id_client_compt')
            elif tipo_empresa_rotina in ['iss', 'icms', 'sem_mov', 'outros', 'todas']:
                grouped_values = valores_df.groupby('id_client_compt').apply(
                    lambda group: group.to_dict(orient='records'))
                main_df['comptsValoresImpostos'] = main_df['id'].map(grouped_values)

            if to_df:
                return main_df
            else:
                return query.all()

    def query_valores_df(self) -> pd.DataFrame:

        with self.Session() as session:
            query = session.query(self.valores_impostos).join(self.orm,
                                                              self.valores_impostos.id_client_compt == self.orm.id).filter(
                self.orm.compt == self.main_compt)
            return self.dba.query_to_dataframe(query)

    def start_new_compt_query(self, another_compt: str, to_df=False) -> Tuple[
        Union[pd.DataFrame, List[sql.orm.Query]], Union[pd.DataFrame, List[sql.orm.Query]]]:
        """
        :param another_compt: based on this compt it will rethrive the data to set a new compt
        :param to_df:
        :return:
        """

        with self.Session() as session:
            query_compts = session.query(self.orm).filter_by(compt=compt_to_date_obj(another_compt))
            empresas_allowed = session.query(self.empresas).filter_by(status_ativo=True)

            # empresa.status_ativo deve ser True
            main_empresas_allowed__ids = [row.id for row in empresas_allowed]
            query_compts = query_compts.filter(self.orm.empresa_id.in_(main_empresas_allowed__ids))
            # query_compts = query_compts.join(self.valores_impostos, self.orm.id == self.valores_impostos.id_client_compt)

            query_compts__ids = [row.id for row in query_compts]
            query_valores = session.query(self.valores_impostos).filter(
                self.valores_impostos.id_client_compt.in_(query_compts__ids))

            if to_df:
                return self.dba.query_to_dataframe(query_compts), self.dba.query_to_dataframe(query_valores)
            else:
                return query_compts.all(), query_valores.all()

    def get_interface_df(self, allowing_impostos_list=None) -> pd.DataFrame:
        _default_order = ["SEM_MOV", "ISS", "ICMS"]
        _main_df = self.query_data_by_routine_in_compt('interface')

        sorted_df = sort_dataframe(_main_df, _default_order, 'imposto_a_calcular')

        if allowing_impostos_list is None or 'LP' not in allowing_impostos_list:
            sorted_df = sorted_df.loc[sorted_df['imposto_a_calcular'] != 'LP']

        if allowing_impostos_list:
            sorted_df = sorted_df.loc[sorted_df['imposto_a_calcular'].isin(allowing_impostos_list)]

        return sorted_df

    # Updates...
    # add new compt
    def _add_new_compt(self) -> None:

        compts_df, valores_df = self.start_new_compt_query(another_compt=get_compt(-2), to_df=True)
        id_mapping = {}

        def if_value_in_then_true(id_client_compt: int, field, should_be_in: list) -> bool:
            """
            :param id_client_compt:
            :param field:
            :param should_be_in:
            :return:
            """
            field_values_list = valores_df.loc[
                (valores_df['id_client_compt'] == id_client_compt), field].to_list()
            exp = [val in should_be_in for val in field_values_list]

            checkup_for_all = all(exp)
            checkup_for_any = any(exp)

            assert checkup_for_all == checkup_for_any, f"Lista de impostos não permitidas no checkup: {field_values_list}, (id_client_compt: {id_client_compt})"

            return checkup_for_all and checkup_for_any

        row_exists = True
        with self.Session() as session:
            # check if the row already exists
            row_exists = session.query(self.orm).filter(
                self.orm.compt == self.main_compt).first()
            if not row_exists:
                print("Init new compt: ", self.main_compt, '-------')
                # create new rows with incremented date

                for _, row in compts_df.iterrows():
                    _envio = if_value_in_then_true(row.id, field='imposto_a_calcular',
                                                   should_be_in=['LP', 'SEM_MOV'])

                    # _declarado = True if str(
                    #     row.imposto_a_calcular) == 'LP' and '//' not in row.ginfess_cod else False
                    _declarado = False

                    new_compt_row = self.orm(
                        empresa_id=row.empresa_id,
                        declarado=_declarado,
                        envio=_envio,
                        compt=self.main_compt,
                        pode_declarar=if_value_in_then_true(row.id, field='imposto_a_calcular',
                                                            should_be_in=['LP', 'SEM_MOV']),
                        venc_das=get_next_venc_das(row.venc_das) if row.venc_das else row.venc_das,
                    )
                    session.add(new_compt_row)
                    # flusha a sessão para gerar ID
                    session.flush()
                    id_mapping[row.id] = new_compt_row.id

                session.commit()

        with self.Session() as session:
            if row_exists:
                return
            for _, row in valores_df.iterrows():
                def get_status_imports_g5(
                        campo: str):
                    campo = '' if campo is None else campo
                    return campo if campo.upper() != 'OK' else ''

                id_client_compt = id_mapping.get(row.id_client_compt)
                if id_client_compt is None:
                    print(row.id_client_compt, 'Não foi encontrado')
                    continue

                new_valores_row = self.valores_impostos(
                    nf_saida_prestador=get_status_imports_g5(row.nf_saida_prestador),
                    nf_entrada_tomador=get_status_imports_g5(row.nf_entrada_tomador),
                    sem_retencao=0.00,
                    com_retencao=0.00,
                    valor_total=0.00,
                    anexo=row.anexo,
                    imposto_a_calcular=row.imposto_a_calcular,
                    id_client_compt=id_mapping.get(row.id_client_compt),
                )
                session.add(new_valores_row)
            session.commit()


if __name__ == '__main__':
    cc = OeClientComptsRepository(compt='08-2023')
    print()
    # me = MainEmpresasRepository()
    # df = cc.query(id=2)
