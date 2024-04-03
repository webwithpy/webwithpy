from __future__ import annotations
from typing import TYPE_CHECKING, Any
import re
from ..core import DB
from ..objects.objects import ReferencedField

if TYPE_CHECKING:
    from ..objects.objects import Operation, Table, DefaultField


class IDialect:
    @classmethod
    def create_table(cls, table_name: str, fields: list[DefaultField]):
        ...

    @classmethod
    def primary_key(cls):
        ...

    @classmethod
    def i_join(cls, table_name: str, where: str) -> str:
        ...

    @classmethod
    def l_join(cls, table_name: str, where: str) -> str:
        ...

    @classmethod
    def get_where_join_stmt(
        cls, table_name: str, join_table_name: str, where_stmt: str, args: list[Any]
    ) -> tuple[str, str, list[Any]]:
        where_parts = re.split("OR|AND", where_stmt)
        on_statements = []
        operators = []
        result = ""
        new_args = []
        var_idx = 0

        for part in where_parts:
            if table_name in part and join_table_name in part:
                on_statements.append(part)
                if part + "AND " in where_stmt:
                    where_stmt = where_stmt.replace(part + "AND ", "")
                    operators.append("AND")
                elif part + "OR " in where_stmt:
                    where_stmt = where_stmt.replace(part + "OR ", "")
                    operators.append("OR")
                else:
                    where_stmt = where_stmt.replace(part, "")

                if "?" in part:
                    new_args.append(args.pop(var_idx))
                    var_idx -= 1

            if "?" in part:
                var_idx += 1

        for idx, part in enumerate(on_statements):
            result += part
            if operators and idx != len(on_statements) - 1:
                result += operators.pop(0)

        where_stmt = where_stmt.rstrip(" OR AND")

        for arg in args:
            new_args.append(arg)

        return result, where_stmt, new_args

    @classmethod
    def get_join_stmt(
        cls,
        table_name: str,
        tables: list[str],
        full_where: str,
        args: list[Any],
    ) -> tuple[str, str, list[Any]]:
        join_stmt = ""

        for join_table_name in tables:
            on_stmt, full_where, args = cls.get_where_join_stmt(
                table_name, join_table_name, full_where, args
            )

            is_inner_join = False
            for stmt in on_stmt.split(" "):
                if table_name in stmt and isinstance(
                    DB.tables[table_name].get_field(stmt.split(".")[1]),
                    ReferencedField,
                ):
                    is_inner_join = True

            if is_inner_join:
                join_stmt += cls.i_join(join_table_name, on_stmt)
            else:
                join_stmt += cls.l_join(join_table_name, on_stmt)

        return join_stmt, full_where, args

    @classmethod
    def select(
        cls,
        query: str,
        tables: list[str],
        select_operation: Operation,
        distinct: bool,
        fields: list[str],
        order_by: Operation,
        group_by: Operation,
        args: list[Any],
    ) -> tuple[str, list[any]]:
        fields = "*" if not fields else ",".join(fields)
        non_join_table = tables.pop(0)
        join, query, args = cls.get_join_stmt(non_join_table, tables, query, args)

        distinct_stmt = "DISTINCT " if distinct else ""
        order_by_stmt = f"ORDER BY {order_by.__str__()}" if order_by else ""
        group_by_stmt = f"GROUP BY {group_by.__str__()}" if group_by else ""

        if select_operation:
            fields = f"{select_operation.__str__()}, " + fields

        where_clause = f"WHERE {query}" if query.strip() else ""

        return (
            f"SELECT {distinct_stmt}{fields} FROM {non_join_table} {join} {where_clause} {group_by_stmt} {order_by_stmt}",
            args,
        )

    @classmethod
    def insert(cls, table: Table, items: dict[str, Any]):
        ...

    @classmethod
    def update(cls, query: str, tables: list[str], items: dict[str, Any]):
        ...

    @classmethod
    def delete(cls, query: str, tables: list[str]):
        ...
