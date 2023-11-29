from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..objects import Field
    from ..query import Query


class IDriver:
    def select_sql(
        self,
        *fields: tuple | int,
        query: Optional[Query] = None,
        table_name: Optional[str] = None,
        distinct: Optional[bool] = False,
        orderby: Field = None,
    ) -> list[str, list]:
        """
        generates a select sql statement with arguments
        returns: str, list
        """
        pass

    def insert(self, table_name: str, items: dict):
        pass

    def update(self, query, **kwargs):
        pass

    def delete(self, query):
        pass

    def translate_unpacked_query_sql(
        self, unpacked_query: dict[str, list[str]]
    ) -> dict[str, set | list | str]:
        pass
