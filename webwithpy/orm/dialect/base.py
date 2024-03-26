from __future__ import annotations
from typing import TYPE_CHECKING, Any

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
    def i_join(cls, table_name, where: str = ""):
        ...

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
    ):
        ...

    @classmethod
    def insert(cls, table: Table, items: dict[str, Any]):
        ...

    @classmethod
    def update(cls, query: str, tables: list[str], items: dict[str, Any]):
        ...

    @classmethod
    def delete(cls, query: str, tables: list[str]):
        ...
