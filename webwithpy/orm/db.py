from .query import Query
from .objects import Table, Field
from .dialects.sqlite import SqliteDialect
from sqlite3 import dbapi2 as sqlite
from pathlib import Path
from typing import Union


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DB:
    cursor = None

    def __init__(self, db_path: Union[Path, str]):
        if isinstance(db_path, str):
            db_path = Path(db_path)

        # make sure the db exists
        db_path.touch()

        self.conn = sqlite.connect(db_path)
        self.conn.row_factory = dict_factory
        DB.cursor = self.conn.cursor()

        self.tables = {}

    def create_table(self, table_name: str, *fields: Field):
        fields = list(fields)
        id_field = Field('id', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        fields.insert(0, id_field)

        for field in fields:
            field.table_name = table_name
            field.cursor = self.cursor
            field.conn = self.conn

        tbl = Table(self.conn, self.cursor, table_name, fields)
        self.tables[table_name] = tbl

        self._create_table(table_name, *fields)

    def _create_table(self, table_name: str, *fields: Field):
        sql = f'CREATE TABLE IF NOT EXISTS {table_name} ('
        for field in fields:
            sql += f'{field.field_name} {field.field_type}, '
        sql = sql[:-2] + ')'
        self.cursor.execute(sql)

    def __getattribute__(self, item):
        try:
            return super(DB, self).__getattribute__(item)
        except Exception as e:
            if item in self.tables.keys():
                return self.tables[item]
            raise e
