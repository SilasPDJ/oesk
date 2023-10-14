from utilities.db import DbAccessManager


class Sql(DbAccessManager):
    def __init__(self):
        super().__init__()

        with self.Session() as session:
            pass








