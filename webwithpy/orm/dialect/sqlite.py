from __future__ import annotations
from .base import IDialect
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..objects.objects import Table, DefaultField, Operation


class SqliteDialect(IDialect):
    @classmethod
    def create_table(cls, table_name, fields: list[DefaultField]):
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        for field in fields:
            sql += f"{field.name} {field.field_type}, "

        sql = sql[:-2] + ")"

        return sql

    @classmethod
    def primary_key(cls):
        return "INTEGER PRIMARY KEY AUTOINCREMENT"

    @classmethod
    def i_join(cls, table_name, where: str = ""):
        if where and not where.startswith(" ON "):
            where += f" ON {where}"
        return f"INNER JOIN {table_name}{where}"

    @classmethod
    def insert(cls, table: Table, items: dict[str, Any]):
        return f"INSERT INTO {table.table_name} ({','.join(items.keys())}) VALUES ({','.join(['?' for _ in items.keys()])})"

    @classmethod
    def select(
        cls,
        query: str,
        tables: list[str],
        select_operation: Operation,
        distinct: bool,
        fields: list[str],
        order_by: Operation,
        group_by: Operation
    ):
        fields = "*" if len(fields) == 0 else ",".join(fields)
        non_join_table = tables.pop(0)
        join = "\n".join([cls.i_join(name) for name in tables])
        distinct_stmt = "DISTINCT " if distinct else ""
        order_by = f"ORDER BY {order_by.__str__()}" if order_by else ""
        group_by = f"GROUP BY {group_by.__str__()}" if group_by else ""

        if select_operation:
            fields = f"{select_operation.__str__()}, " + fields

        return f"SELECT {distinct_stmt}{fields} FROM {non_join_table} {join} WHERE {query} {group_by} {order_by}"

    @classmethod
    def update(cls, query: str, tables: list[str], items: dict[str, Any]):
        if len(tables) > 1:
            raise Exception("Updating multiple tables is not allowed!")

        update_stmt = ",".join([f"{key}=?" for key in items.keys()])
        return f"UPDATE {tables[0]} SET {update_stmt} WHERE {query}"

    @classmethod
    def delete(cls, query: str, tables: list[str]):
        if len(tables) > 1:
            raise Exception("Updating multiple tables is not allowed!")

        return f"DELETE FROM {tables[0]} WHERE {query}"
