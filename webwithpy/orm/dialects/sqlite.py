from .sql import SQLDialect
from ..query import Query


class SqliteDialect(SQLDialect):
    @classmethod
    def unpack(cls, query: Query) -> dict:
        """
        unpacks a sqlite query statement
        """
        unpacked_query = {"fields": [], "stmts": []}

        def _unpack(part):
            if isinstance(part, Query):
                unpacked = cls.unpack(part)
                unpacked_query["fields"] += unpacked["fields"]
                unpacked_query["stmts"] += unpacked["stmts"]
            else:
                unpacked_query["fields"].append(part)

        _unpack(query.first)
        unpacked_query["stmts"].append(query.operator)
        _unpack(query.second)

        return unpacked_query
