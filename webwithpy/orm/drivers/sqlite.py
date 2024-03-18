from __future__ import annotations

from ..drivers.driver import IDriver, dict_factory
from ..helpers.settings import DBSettings
from ..objects.query import Query, ListedQuery
from ..core import DB

from sqlite3 import dbapi2 as sqlite
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..objects.objects import Table


class SqliteDriver(IDriver):
    def __init__(self, db_settings: DBSettings) -> None:
        super().__init__(db_settings)
        self.connect()
        self.setup()

    def connect(self) -> None:
        self.conn = sqlite.connect(self.settings.path, timeout=10)

    def setup(self):
        self.conn.row_factory = dict_factory

    def execute_sql(self, sql: str, items: list = None):
        if not self.conn:
            self.connect()
            self.setup()

        if not items:
            items = []

        result = self.conn.execute(sql, items).fetchall()
        self.conn.commit()
        return result

    def insert(self, table: Table, items: dict) -> None:
        sql = DB.dialect.insert(table, items)
        self.execute_sql(sql, list(items.values()))

    def select(self, query: Query | ListedQuery, fields: list[str] = None) -> list[Any]:
        if fields is None:
            fields = []

        s_fields, stmt = query.build()
        sql = DB.dialect.select(stmt, query.__tables__(), False, fields)

        return self.execute_sql(sql, s_fields)

    def update(self, query: Query | ListedQuery, update_values: dict) -> None:
        fields, stmt = query.build()
        sql = DB.dialect.update(stmt, query.__tables__(), update_values)

        update = list(update_values.values())
        update += fields

        self.execute_sql(sql, update)

    def delete(self, query: Query | ListedQuery):
        fields, stmt = query.build()
        sql = DB.dialect.delete(stmt, query.__tables__())

        self.execute_sql(sql, fields)
