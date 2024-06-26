from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .objects import DefaultField, Operation
    from ..drivers.driver import IDriver


class IQuery:
    def __init__(self, driver: IDriver):
        self.driver = driver

    @classmethod
    def is_field(cls, var: DefaultField | Any):
        return "Field" in var.__class__.__name__

    def build(self) -> [list, str]:
        ...

    def __tables__(self) -> list[str]:
        ...

    def select(
        self,
        fields: list[str] = None,
        select_operation: Operation = None,
        order_by: Operation = None,
        group_by: Operation = None,
        debug: bool = False,
    ):
        """
        :param fields: list of fields to select in query
        :param select_operation: key is the type of operation like 'COUNT' and value is the field to perform the
         operation on
        :param order_by: order list by parameter
        :param group_by: group list by parameter
        """
        fields = [] if not fields else fields

        return self.driver.select(
            query=self,
            fields=fields,
            select_operation=select_operation,
            order_by=order_by,
            group_by=group_by,
            debug=debug,
        )

    def update(self, **items: Any) -> None:
        self.driver.update(self, items)

    def delete(self):
        self.driver.delete(self)


class ListedQuery(IQuery):
    def __init__(self, driver: IDriver, q1: Query, q2: Query, op: str) -> None:
        super().__init__(driver)
        self.queries = [q1, q2]
        self.ops = [op]

    def build(self) -> [list, str]:
        fields = []
        res = ""
        for q in self.queries:
            q_fields, build_res = q.build()
            fields += q_fields
            res += build_res

            if self.ops:
                res += f"{self.ops.pop(0)} "

        return fields, res

    def __tables__(self) -> list[str]:
        tables = []
        for query in self.queries:
            for table in query.__tables__():
                if table not in tables:
                    tables.append(table)
        return tables

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


class Query(IQuery):
    def __init__(
        self,
        driver: IDriver,
        field1: DefaultField | Any,
        field2: DefaultField | Any,
        op: str,
    ):
        """
        :param field1: first field in the query, can be a field from a table or another python datatype like int
        :param field2: first field in the query, can be a field from a table or another python datatype like int
        :param op: the operation that will be done in sql like '<='
        """
        super().__init__(driver)
        self.field1 = field1
        self.field2 = field2
        self.op = op

    @staticmethod
    def translate_none_operator(field: str, op: str):
        if field is None and op == "!=":
            op = "IS NOT"
        elif field is None and op == "=":
            op = "IS"

        return op

    def build(self) -> [list, str]:
        fields = []
        res = ""

        self.op = self.translate_none_operator(self.field2, self.op)

        if not self.is_field(self.field1):
            fields.append(self.field1)
            res += f"? {self.op} "
        else:
            res += f"{self.field1} {self.op} "

        if not self.is_field(self.field2):
            fields.append(self.field2)
            res += f"?"
        else:
            res += f"{self.field2} "

        return fields, res

    def __tables__(self) -> list[str]:
        tables = []
        if self.is_field(self.field1):
            tables.append(self.field1.table_name)
        if self.is_field(self.field2):
            if self.field2.table_name not in tables:
                tables.append(self.field2.table_name)

        return tables

    def __and__(self, other: Query | ListedQuery) -> ListedQuery:
        if isinstance(other, Query):
            return ListedQuery(self.driver, self, other, "AND")
        elif isinstance(other, ListedQuery):
            other.__and__(self)
            return other

        raise TypeError(f"Unsupported operand type Query and {type(other)}")

    def __or__(self, other: Query | ListedQuery) -> ListedQuery:
        if isinstance(other, Query):
            return ListedQuery(self.driver, self, other, "OR")
        elif isinstance(other, ListedQuery):
            other.__or__(self)
            return other

        raise TypeError(f"Unsupported operand type Query and {type(other)}")
