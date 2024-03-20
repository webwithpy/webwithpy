from __future__ import annotations
from ..helpers.settings import DBSettings
from ..core import DB
from .driver import IDriver
from typing import TYPE_CHECKING, Any
from mysql.connector import Connect

import bcrypt

if TYPE_CHECKING:
    from ..objects.query import ListedQuery, Query
    from ..objects.objects import DefaultField, Table


class MysqlDriver(IDriver):
    def __init__(self, settings: DBSettings) -> None:
        super().__init__(settings)
        self.connect()
        self.setup()

    def connect(self):
        self.conn = Connect(
            host=self.settings.hostname,
            user=self.settings.username,
            password=self.settings.password,
            database=self.settings.database,
        )

    def execute_sql(self, sql: str, params: list[str] = None) -> Any:
        if not params:
            params = []

        cursor = self.conn.cursor(prepared=True, dictionary=True)
        cursor.execute(sql, params)
        res = cursor.fetchall()
        cursor.close()
        self.conn.commit()
        return res

    def insert(self, table: Table, items: dict) -> None:
        sql = DB.dialect.insert(table, items)

        for field_name in items.keys():
            field = DB.tables[table.name].get_field(field_name)
            if field.encrypt:
                salt = bcrypt.gensalt()
                # Hashing the password
                hashed = bcrypt.hashpw(items[field_name], salt)
                items[field_name] = hashed

        self.execute_sql(sql, list(items.values()))

    def select(
        self,
        query: Query | ListedQuery,
        fields: list[str] = None,
        order_by: DefaultField = None,
    ) -> list[Any]:
        s_fields, stmt = query.build()
        sql = DB.dialect.select(stmt, query.__tables__(), False, fields, order_by)

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
