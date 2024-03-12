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

empresas_servicos, empresas_gias, empresas_icms, oe_empresas, main_empresas, clients_compts = OrmTables.get_classes().values()


class OeEmpresasRepository(RepositoryUtils):
    def __init__(self):
        self.dba = DbAccessManager()
        self.Session = self.dba.Session
        self.orm = OrmTables.OEEmpresas
        super().__init__(self.orm, self.Session)


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


class ClientComptsRepository(RepositoryUtils):
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

        self._add_new_compt()

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

        :param must_be_authorized: Filter by 'pode_declarar'. Defaults to False
        :param must_have_status_ativo: Filter by 'status_ativo'. Defaults to True.
        :param to_df: If True, return a DataFrame; if False, return a list of ORM queries.
        :return: Either a DataFrame or a list of ORM queries.
        """
        tipo_empresa_rotina = tipo_empresa_rotina.lower().strip()
        assert tipo_empresa_rotina in ['sem_mov', 'iss', 'icms', 'gias', 'outros',
                                       'todas'], 'tipo_empresa_rotina inválido'

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
            elif tipo_empresa_rotina == 'todas':
                query = session.query(self.orm, self.empresas).filter_by(compt=self.main_compt)
                query = query.join(self.empresas, self.orm.empresa_id == self.empresas.id)
            else:
                raise ValueError("Surgiram outros...")

            if must_be_authorized:
                query = query.filter_by(pode_declarar=True)
            if must_have_status_ativo:
                query = query.filter_by(status_ativo=True)
            if to_df:
                return self.dba.query_to_dataframe(query)
            else:
                return query.all()

    def start_new_compt_query(self, another_compt: str, to_df=False) -> Union[pd.DataFrame, List[sql.orm.Query]]:
        """
        :param another_compt: based on this compt it will rethrive the data to set a new compt
        :return:
        """

        with self.Session() as session:
            query = session.query(self.orm).filter_by(compt=compt_to_date_obj(another_compt))
            empresas_allowed = session.query(self.empresas).filter_by(status_ativo=True)

            # empresa.status_ativo deve ser True
            main_empresas_allowed__ids = [row.id for row in empresas_allowed]
            query = query.filter(self.orm.empresa_id.in_(main_empresas_allowed__ids))

            if to_df:
                return self.dba.query_to_dataframe(query)
            else:
                return query.all()

    def get_interface_df(self, allowing_impostos_list=None) -> pd.DataFrame:
        _default_order = ["SEM_MOV", "ISS", "ICMS"]
        _main_df = self.query_data_by_routine_in_compt('todas')

        sorted_df = sort_dataframe(_main_df, _default_order, 'imposto_a_calcular')

        if allowing_impostos_list is None or 'LP' not in allowing_impostos_list:
            sorted_df = sorted_df.loc[sorted_df['imposto_a_calcular'] != 'LP']

        if allowing_impostos_list:
            sorted_df = sorted_df.loc[sorted_df['imposto_a_calcular'].isin(allowing_impostos_list)]

        return sorted_df

    # Updates...
    # add new compt
    def _add_new_compt(self) -> None:
        with self.Session() as session:
            # check if the row already exists
            row_exists = session.query(self.orm).filter(
                self.orm.compt == self.main_compt).first()
            if not row_exists:
                print("Init new compt: ", self.main_compt, '-------')
                # create new rows with incremented date

                for row in self.start_new_compt_query(another_compt=get_compt(-2)):
                    _envio = True if str(
                        row.imposto_a_calcular) == 'LP' else False

                    # _declarado = True if str(
                    #     row.imposto_a_calcular) == 'LP' and '//' not in row.ginfess_cod else False
                    _declarado = False

                    def get_status_imports_g5(
                            campo: str):
                        campo = '' if campo is None else campo
                        return campo if campo.upper() != 'OK' else ''

                    new_row = self.orm(
                        main_empresa_id=row.main_empresa_id,
                        empresa_id=row.empresa_id,
                        declarado=_declarado,
                        nf_saidas=get_status_imports_g5(row.nf_saidas),
                        nf_entradas=get_status_imports_g5(row.nf_entradas),
                        sem_retencao=0.00,
                        com_retencao=0.00,
                        valor_total=0.00,
                        anexo=row.anexo,
                        imposto_a_calcular=row.imposto_a_calcular,
                        compt=self.main_compt,
                        envio=_envio,
                        pode_declarar=False if row.imposto_a_calcular != "SEM_MOV" else True,
                        venc_das=get_next_venc_das(row.venc_das) if row.venc_das else row.venc_das,
                    )
                    session.add(new_row)
                session.commit()


if __name__ == '__main__':
    cc = ClientComptsRepository(compt='08-2023')
    cc.get_g5_df()
    print()
    # me = MainEmpresasRepository()
    # df = cc.query(id=2)
