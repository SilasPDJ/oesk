import pandas as pd

class RepositoryUtils:
    def __init__(self, orm, session):
        self.orm = orm
        self.Session = session

    @property
    def _orm_columns(self) -> list:
        return [column.name for column in self.orm.__table__.columns]

    def get_as_orm(self, **kwargs):
        """
        Sobrescreva para settar os kwargs defaults... (conforme em ComptsRepository)
        ### mapping single database records... or list of
        """
        with self.Session() as session:
            query = session.query(self.orm).filter_by(**kwargs)
            data = query.one_or_none()
            return data

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

    def update_from_object(self, orm_object):
        with self.Session() as session:
            session.merge(orm_object)
            session.commit()

