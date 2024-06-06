import time

import pandas as pd
from sqlalchemy import inspect


# TODO descobrir pq todos menos o from_object nao estão funcionando

def _to_snaked_case(s):
    _case = ''
    for i, char in enumerate(s):
        if i != 0 and char.isupper():
            _case += '_' + char.lower()
        else:
            _case += char.lower()
    return _case


def to_camel_case(data: dict) -> dict:
    return {
        ''.join(word.title() if i > 0 else word for i, word in enumerate(key.split('_'))): value
        for key, value in data.items()
    }


class RepositoryUtils:
    def __init__(self, orm, session):
        self.orm = orm
        self.Session = session

    @property
    def _orm_columns(self) -> list:
        return [column.name for column in self.orm.__table__.columns]

    @staticmethod
    def flatten_list(lst: list):
        return [item for sublist in lst for item in (sublist if isinstance(sublist, list) else [sublist])]

    def get_as_orm(self, **kwargs):
        """
        Sobrescreva para settar os kwargs defaults... (conforme em ComptsRepository)
        ### mapping single database records... or list of
        """
        with self.Session() as session:
            query = session.query(self.orm).filter_by(**kwargs)
            data = query.one_or_none()
            return data

    def get_pk(self) -> str:
        """
        :return: the primary key
        """
        return inspect(self.orm).primary_key[0].name

    # methods for updates in a db table
    def update_from_dataframe(self, df: pd.DataFrame):
        """Updates a database's table based on a dataframe, (allows multiple rows)"""
        with self.Session() as session:
            for row in df.itertuples(index=False):
                # preventing data from joins
                data_to_orm = {column: getattr(row, column) for column in self._orm_columns}

                session.merge(self.orm(**data_to_orm))
                # session.merge(self.orm(**row._asdict()))
            session.commit()

    def update_from_pandas_object(self, pd_obj):
        with self.Session() as session:
            data_to_orm = {column: getattr(pd_obj, column) for column in self._orm_columns}
            session.merge(self.orm(**data_to_orm))
        session.commit()

    def update_from_dictionary(self, dictionary: dict):
        """update a database's table based on a dictionary, (once per time)"""
        with self.Session() as session:
            # preventing data from joins
            dict_to_orm = {key: dictionary[key] for key in self._orm_columns if key in dictionary}
            session.merge(self.orm(**dict_to_orm))
            # session.merge(self.orm(**dictionary))
            session.commit()

    # integração inicial com appian, mantendo local e online por enquanto
    def insert_objects_if_not_exist(self, objects_list: list[dict]):
        with self.Session() as session:
            # gets first value as id
            existing_ids = [getattr(obj, self.get_pk()) for obj in session.query(self.orm).filter(
                getattr(self.orm, self.get_pk()).in_([list(obj.values())[0] for obj in objects_list])).all()]

            new_ids_found = [list(obj.values())[0] for obj in objects_list if list(obj.values())[0] not in existing_ids]
            for _obj in objects_list:

                # transforma para o que o banco de dados ta esperando, a api devolve cammel cased
                new_obj = {_to_snaked_case(key): value for key, value in _obj.items() if
                           _to_snaked_case(key) in self._orm_columns}

                new_orm_object = self.orm(**new_obj)
                _obj_id_value = new_obj.get(self.get_pk())

                # Se o id já existir cadastrado, atualiza
                if _obj_id_value in existing_ids:
                    existing_object = session.query(self.orm).filter(
                        getattr(self.orm, self.get_pk()) == _obj_id_value).first()
                    for key, value in new_obj.items():
                        if key != _obj_id_value:
                            setattr(existing_object, key, value)
                    session.merge(existing_object)
                # Se o id for novo, será inserido
                elif new_ids_found:
                    if _obj_id_value in new_ids_found:
                        session.add(new_orm_object)
            session.commit()

    def insert_compts_if_exists_update(self, objects_list: list[dict], valores):
        # TODO......... VALORES
        with self.Session() as session:
            # gets first value as id
            for _obj in objects_list:
                if _obj.get('compt'):
                    _obj['compt'] = _obj['compt'][:-1]
                    _obj['vencDas'] = _obj['vencDas'] if not _obj['vencDas'] else _obj['vencDas'][:-1]
                    new_obj = {_to_snaked_case(key): value for key, value in _obj.items() if
                               _to_snaked_case(key) in self._orm_columns}
                    existing_results = session.query(self.orm)
                    existing_results = existing_results.filter_by(compt=new_obj.get('compt'),
                                                                  empresa_id=new_obj.get('empresa_id'))
                    existing_results = existing_results.all()

                    orm_obj = self.orm(**new_obj)
                    if existing_results:
                        session.merge(orm_obj)
                    else:
                        session.add(orm_obj)

            session.commit()
