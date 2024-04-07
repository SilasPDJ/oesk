from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy import Integer, String, Numeric, Date
from sqlalchemy.orm import Mapper, class_mapper

from utilities.db import DbAccessManager

Base = declarative_base()


class OrmTables:
    # parte da integração
    class ClientsCompts(Base):
        __tablename__ = 'oe_clients_compts'

        id = Column(Integer, primary_key=True)

        empresa_id = Column(Integer, ForeignKey('oe_empresas.id'))
        empresa = relationship(
            "OEEmpresas", back_populates="clients_compts")

        declarado = Column(Boolean())
        envio = Column(Boolean())
        compt = Column(Date())
        pode_declarar = Column(Boolean())
        venc_das = Column(Date())

        compts_valores_impostos = relationship("ComptsValoresImpostos", back_populates="clients_compts")

        def __repr__(self):
            return f"{self.id} - {self.empresa_id:03d} - {self.empresa.razao_social}"

    class ComptsValoresImpostos(Base):
        __tablename__ = 'oe_compts_valores_impostos'

        id = Column(Integer, primary_key=True)
        nf_saida_prestador = Column(String(30))
        nf_entrada_tomador = Column(String(30))
        sem_retencao = Column(Numeric(precision=10, scale=2), default=0.00)
        com_retencao = Column(Numeric(precision=10, scale=2), default=0.00)
        valor_total = Column(Numeric(precision=10, scale=2), default=0.00)
        anexo = Column(String(3))
        imposto_a_calcular = Column(String(7))
        id_client_compt = Column(Integer, ForeignKey('oe_clients_compts.id'))

        clients_compts = relationship("ClientsCompts", back_populates="compts_valores_impostos")

        def __repr__(self):
            return f"ComptsValoresImpostos(id={self.id}, nf_saida_prestador={self.nf_saida_prestador}, nf_entrada_tomador={self.nf_entrada_tomador}, ...)"

    class OEEmpresas(Base):
        __tablename__ = 'oe_empresas'

        id = Column(Integer, primary_key=True)
        razao_social = Column(String(255))
        cnpj = Column(String(18), unique=True)
        cpf = Column(String(14))
        codigo_simples = Column(String(12))
        email = Column(String(255))
        ha_procuracao_ecac = Column(String(15))
        status_ativo = Column(Boolean())

        oe_servicos = relationship("OEServicos", back_populates="empresa")
        oe_gias = relationship("OEGias", back_populates="empresa")
        oe_icms__sem_mov = relationship("OEEmpresasICMS_SemMov", back_populates="empresa")

        clients_compts = relationship(
            "ClientsCompts", back_populates="empresa")

        def __repr__(self):
            return f"<oe_empresas(cnpj='{self.cnpj}', razao_social='{self.razao_social}')>"

    class OEEmpresasICMS_SemMov(Base):
        """ 'outras' Empresas """
        __tablename__ = 'oe_icms__sem_mov'

        id = Column(Integer, ForeignKey('oe_empresas.id'), primary_key=True)
        razao_social = Column(String(255))
        cnpj = Column(String(18), unique=True)
        cpf = Column(String(14))
        codigo_simples = Column(String(12))
        email = Column(String(255))
        ha_procuracao_ecac = Column(String(15))
        status_ativo = Column(Boolean())

        empresa = relationship("OEEmpresas", back_populates="oe_icms__sem_mov")

        def __repr__(self):
            return f"<oe_icms__sem_mov(cnpj='{self.cnpj}', razao_social='{self.razao_social}')>"

    class OEServicos(Base):
        __tablename__ = 'oe_servicos'

        id_servico = Column(Integer, primary_key=True, autoincrement=True)
        login = Column(String(50))
        password = Column(String(50))
        giss_login = Column(String(20))
        inscricao_municipal = Column(String(50))
        nfs_login_link = Column(String(500), nullable=False)
        empresa_id = Column(Integer, ForeignKey('oe_empresas.id'), unique=True)

        empresa = relationship("OEEmpresas", back_populates="oe_servicos")

    class OEGias(Base):
        __tablename__ = 'oe_gias'

        id_gia = Column(Integer, primary_key=True, autoincrement=True)
        login = Column(String(20), nullable=False)
        password = Column(String(100), nullable=False)
        inscricao_estadual = Column(String(15))
        empresa_id = Column(Integer, ForeignKey('oe_empresas.id'), unique=True)

        empresa = relationship("OEEmpresas", back_populates="oe_gias")
        ativa = Column(Boolean())

    @classmethod
    def get_classes(cls) -> dict:
        classes = [eval(f"OrmTables.{class_name}") for class_name in dir(cls) if
                   isinstance(getattr(cls, class_name), type)][::-1][1:]
        obj = {_class.__tablename__: _class for _class in classes}
        return obj


if __name__ == '__main__':
    dam = DbAccessManager()
    Base.metadata.create_all(dam.engine)
