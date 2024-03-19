from __future__ import annotations
from ..helpers.settings import DBSettings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..objects.query import ListedQuery, Query
    from ..objects.objects import DefaultField, Table


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class IDriver:
    def __init__(self, settings: DBSettings) -> None:
        self.settings = settings
        self.conn = None

    def connect(self):
        ...

    def setup(self):
        ...

    def execute_sql(self, sql: str, params: list[str] = None) -> Any:
        ...

    def insert(self, table: Table, items: dict) -> None:
        ...

    def select(
        self,
        query: Query | ListedQuery,
        fields: list[str] = None,
        order_by: DefaultField = None,
    ) -> list[Any]:
        ...

    def update(self, query: Query | ListedQuery, update_values: dict) -> None:
        ...

    def delete(self, query: Query | ListedQuery):
        ...
