"""
The webwithpy ORM will only work with sqlite and won't be expanded for a while.
However if you ever want to use a different ORM you can just ignore this one and work with a different ORM.
"""
from .objects import Field
from sqlite3 import dbapi2 as sqlite, Connection
from pathlib import Path
from os import PathLike
from typing import Union, List


class Table:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields or []


class DB:
    def __init__(self, db_path: Union[str, Path, PathLike]):
        if not isinstance(db_path, Path):
            db_path = Path(db_path)

        self.conn: Connection = None
        self.db_path = db_path
        self.tables: List[Table] = []

        self.create_connection()
        self.test_connection()

    def test_connection(self):
        self.conn.execute("SELECT 1;")

    def create_connection(self):
        # Make sure the db path actually exists
        self.db_path.touch()
        self.conn = sqlite.connect(str(self.db_path)).cursor()

    def define_table(self, table_name: str, *fields: List[Field]):
        new_table = Table(table_name, fields)
        for field in fields:
            new_table.__setattr__(field.)
        self.tables.append(new_table)

    def __find_table(self, table_name) -> Table:
        for table in self.tables:
            if table.name == table_name:
                return table

        return None

    def __getattribute__(self, item):
        try:
            return super(DB, self).__getattribute__(item)
        except AttributeError as e:
            tbl = self.__find_table(item)
            if tbl is None:
                print("?")
                raise e
            return tbl
