"""
The webwithpy ORM will only work with sqlite and won't be expanded for a while.
However if you ever want to use a different ORM you can just ignore this one and work with a different ORM.
"""
from .helpers.SQLHelper import SqlHelper as SQLHelper
from .objects import Table, Field
from sqlite3 import dbapi2 as sqlite, Connection
from pathlib import Path
from os import PathLike
from typing import Union, Dict, List


class DB:
    def __init__(self, db_path: Union[str, Path, PathLike]):
        if not isinstance(db_path, Path):
            db_path = Path(db_path)

        self.conn: Connection = None
        self.db_path = db_path
        self.tables: Dict[str, Table] = {}

        self.create_connection()
        self.test_connection()

    def test_connection(self):
        self.conn.execute("SELECT 1;")

    def create_connection(self):
        """
        creates a connection when the database is created
        """
        # Make sure the db path actually exists
        self.db_path.touch()
        self.conn = sqlite.connect(str(self.db_path))
        self.conn.row_factory = SQLHelper.dict_factory
        self.conn = self.conn.cursor()

    def define_table(self, table_name: str, *fields: Field, migrate: bool = True,):
        """
        create table in database based on the table_name and fields
        """
        fields = list(fields)

        # TODO: make optional primary key, this is currently impossible
        prime_field = Field('id', "INTEGER PRIMARY KEY AUTOINCREMENT")
        prime_field = self.__init_field(table_name, prime_field)
        fields.insert(0, prime_field)

        new_table = Table(name=table_name, fields=fields, migrate=migrate)

        for field in fields:
            field = self.__init_field(table_name, field)

        self.tables[table_name] = new_table

        if migrate:
            # remove the table if the table exists
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name};")
            # create the table with all of the fields in the table
            create_table_sql = SQLHelper.create_table_stmt(new_table)
            self.conn.execute(create_table_sql)

    def __init_field(self, tbl_name: str, field: Field) -> Field:
        field.conn = self.conn
        field.table_name = tbl_name
        return field

    def __find_table(self, table_name) -> Table:
        return self.tables[table_name]

    def __getattribute__(self, item):
        try:
            return super(DB, self).__getattribute__(item)
        except AttributeError as e:
            tbl = self.__find_table(item)
            if tbl is None:
                raise e
            return tbl