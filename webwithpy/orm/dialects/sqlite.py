from .sql import SQLDialect
from ..query import Query


class SqliteDialect(SQLDialect):
    @classmethod
    def unpack(cls, query: Query) -> dict:
        def recursive_unpack(q):
            if isinstance(q, Query):
                fields, stmts = recursive_unpack(q.first) + q.operator + recursive_unpack(q.second)
                return fields, stmts
            else:
                return [q], []

        fields, stmts = recursive_unpack(query)
        return {'fields': fields, 'stmts': stmts}
