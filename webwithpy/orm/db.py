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
    conn = None
    cursor = None

    def __init__(self, db_path: Union[Path, str]):
        if DB.conn is None and DB.cursor is None:
            if isinstance(db_path, str):
                db_path = Path(db_path)

            # make sure the db exists
            db_path.touch()

            self.conn = sqlite.connect(db_path)
            self.conn.row_factory = dict_factory

            DB.conn = self.conn
            DB.cursor = self.conn.cursor()
        else:
            # if 2 db objects are created we want to make sure we use the same conn
            self.cursor = DB.cursor
            self.conn = DB.conn

        self.tables = {}

    def create_tables(self):
        id_field = Field(field_type="INTEGER PRIMARY KEY AUTOINCREMENT")

        for table in Table.__subclasses__():
            table_name = (
                table.table_name if "table_name" in vars(table) else table.__name__
            )

            table_fields = {
                var: vars(table)[var]
                for var in vars(table)
                if isinstance(vars(table)[var], Field)
            }

            table_fields["id"] = id_field

            for field_name, field in table_fields.items():
                field.field_name = field_name
                field.table_name = table_name
                field.cursor = self.cursor
                field.conn = self.conn

            tbl = Table(
                self.conn,
                self.cursor,
                table_name,
                [value for value in table_fields.values()],
            )

            self.tables[table_name] = tbl
            self._create_table(table_name, *[field for field in table_fields.values()])

    def _create_table(self, table_name: str, *fields: Field):
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for field in fields:
            sql += f"{field.field_name} {field.field_type}, "
        sql = sql[:-2] + ")"
        self.cursor.execute(sql)

    def __getattribute__(self, item):
        try:
            return super(DB, self).__getattribute__(item)
        except Exception as e:
            if item in self.tables.keys():
                return self.tables[item]
            raise e
