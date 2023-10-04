from .sql import SQLDialect
from ..query import Query


class SqliteDialect(SQLDialect):
    @classmethod
    def unpack(cls, query: Query) -> dict:
        return cls._unpack(query)

    @classmethod
    def _unpack(cls, query: Query) -> dict:
        unpacked_query = {'fields': [], 'stmts': []}

        if isinstance(query.first, Query):
            unpacked = cls._unpack(query.first)
            unpacked_query['fields'] += unpacked['fields']
            unpacked_query['stmts'] += unpacked['stmts']
        else:
            unpacked_query['fields'].append(query.first)

        unpacked_query['stmts'].append(query.operator)

        if isinstance(query.second, Query):
            unpacked = cls._unpack(query.second)
            unpacked_query['fields'] += unpacked['fields']
            unpacked_query['stmts'] += unpacked['stmts']
        else:
            unpacked_query['fields'].append(query.second)

        return unpacked_query
