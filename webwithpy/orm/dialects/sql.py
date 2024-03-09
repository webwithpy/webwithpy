from webwithpy.orm.query import Query


class SQLDialect:
    """
    default sql dialect
    """

    equals = "="
    and_ = "AND"
    or_ = "OR"
    neq = "!="
    lt = "<"
    le = "<="
    gt = ">"
    ge = ">="

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

    def insert(self, table_name: str, items: dict):
        # raise not implemented bc wrong dialect is being used
        raise NotImplemented

    def select(self, fields, tables, where=None, distinct=None, orderby=None):
        # raise not implemented bc wrong dialect is being used
        raise NotImplemented

    def update(self, first_table: str, update_vals: str, where: str):
        # raise not implemented bc wrong dialect is being used
        raise NotImplemented

    def delete(self, first_table: str, select: str):
        # raise not implemented bc wrong dialect is being used
        raise NotImplemented


