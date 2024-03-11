from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ...orm.objects import DefaultField

if TYPE_CHECKING:
    from ..core import DB


class ListedQuery:
    def __init__(self, db: DB, q1: Query, q2: Query, op: str) -> None:
        self.db = db
        self.queries = [q1, q2]
        self.ops = [op]

    def _add_query(self, q: Query, op: str) -> None:
        self.queries.append(q)
        self.ops.append(op)

    def __and__(self, other: Query) -> ListedQuery:
        if isinstance(other, Query):
            self._add_query(other, "AND")
            return self

        raise TypeError(f"Unsupported operand type ListedQuery and {type(other)}")

    def __or__(self, other: Query) -> ListedQuery:
        if isinstance(other, Query):
            self._add_query(other, "OR")
            return self

        raise TypeError(f"Unsupported operand type ListedQuery and {type(other)}")


class Query:
    def __init__(
        self, db: DB, field1: DefaultField | Any, field2: DefaultField | Any, op: str
    ):
        """
        :param field1: first field in the query, can be a field from a table or another python datatype like int
        :param field2: first field in the query, can be a field from a table or another python datatype like int
        :param op: the operation that will be done in sql like '<='
        """
        self.field1 = field1
        self.field2 = field2
        self.op = op
        self.db = db

    def __and__(self, other: Query | ListedQuery) -> ListedQuery:
        if isinstance(other, Query):
            return ListedQuery(self.db, self, other, "AND")
        elif isinstance(other, ListedQuery):
            other.__and__(self)
            return other

        raise TypeError(f"Unsupported operand type Query and {type(other)}")

    def __or__(self, other: Query | ListedQuery) -> ListedQuery:
        if isinstance(other, Query):
            return ListedQuery(self.db, self, other, "OR")
        elif isinstance(other, ListedQuery):
            other.__or__(self)
            return other

        raise TypeError(f"Unsupported operand type Query and {type(other)}")
