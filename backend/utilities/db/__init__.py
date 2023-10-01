import os
from typing import Union

import pandas as pd
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker

load_dotenv()


class DbAccessManager:
    """
    """
    def __init__(self):
        self.engine = self._create_engine()
        self.Session = sessionmaker(bind=self.engine)

    def _create_engine(self):
        MYSQL_HOST = os.getenv('MYSQL_HOST')
        MYSQL_USER = os.getenv('MYSQL_USER')
        MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
        MYSQL_DB = os.getenv('MYSQL_DB')
        MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
        database_url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        return sqlalchemy.create_engine(database_url)

    def query_to_dataframe(self, query_result: Union[
        sqlalchemy.orm.Query, sqlalchemy.engine.cursor.CursorResult]) -> pd.DataFrame:
        # Convert the query result to a pandas DataFrame
        try:
            # sql query to dataframe
            return pd.DataFrame(query_result.fetchall())
        except AttributeError:
            # sqlalchemy orm to dataframe
            return pd.read_sql(query_result.statement, query_result.session.bind)

    def query(self, sql_query: str) -> pd.DataFrame:
        with self.Session() as session:
            try:
                result = session.execute(sqlalchemy.text(sql_query))
                return self.query_to_dataframe(result)
            except Exception as e:
                print(f"Query error: {e}")
                return pd.DataFrame()


if __name__ == '__main__':
    from models import OrmTables
    # Initialize the data access manager
    # data_access_manager = dam
    dam = DbAccessManager()
    main_empresas, clients_compts = OrmTables.get_classes().values()
    # Get ORM classes
    with dam.Session() as session:

        result = session.query(main_empresas).all()

        df = dam.query_to_dataframe(
            session.query(main_empresas).filter_by(id=1))
        dd = dam.query("SELECT * from main_empresas")
        # Print the result
        print(result)
