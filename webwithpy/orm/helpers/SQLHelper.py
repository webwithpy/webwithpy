from sqlite3 import Connection


class SqlHelper:
    def __init__(self):
        ...

    @classmethod
    def get_fields_by_tbl(
        cls, cursor: Connection, table_name, where_expr, self, other
    ):
        return cursor.execute(
            f"""
            SELECT * FROM {table_name}
                WHERE {self} {where_expr} {other}
        """
        ).fetchall()

    @classmethod
    def dict_factory(cls, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @classmethod
    def create_table_stmt(cls, table):
        create_sql_stmt = f"""CREATE TABlE IF NOT EXISTS {table.name}\n("""

        for field in table.fields:
            create_sql_stmt += f"\n     {field.name} {field.type},"

        # we do a [:-1] here to rm the last comma
        return create_sql_stmt[:-1] + "\n);"
