from ..objects import Field
from .driver_interface import IDriver

# No @override, only python >3.12 supports it and wwp currently support >3.10


class SqliteDriver(IDriver):
    def __init__(self, dialect):
        self.dialect = dialect

        # removes the amount of table from the select bc they are already selected
        self.tables_selected = 0

    def select_sql(
        self,
        *fields: tuple | int,
        query=None,
        table_name=None,
        distinct=False,
        orderby=None,
    ):
        # check which fields we will need to select, if fields aren't specified select None
        fields = [str(field) for field in fields] if len(fields) != 0 else "*"

        # unpack query statement so we can translate it to valid sql
        unpacked_query = self.dialect.unpack(query)

        # translate unpacked query to [tables, args, where_stmt]
        sql_information: dict[
            str, set | list | str
        ] = self.translate_unpacked_query_sql(unpacked_query)

        join = (
            table_name
            if len(sql_information["tables"]) == 0
            else sql_information["tables"].pop(0)
        )

        if len(sql_information["tables"]) > 0:
            join += self._tables_to_join(sql_information["tables"])

        # if there is a where statement, add it to the join statement
        fields = ", ".join(fields) if isinstance(fields, list) else fields
        distinct = "DISTINCT " if distinct else ""
        orderby = f"ORDER BY {orderby}" if orderby else ""

        return (
            self._select(
                fields=fields,
                tables=join,
                where=sql_information["where_stmt"],
                distinct=distinct,
                orderby=orderby,
            ),
            sql_information["args"],
        )

    def update(self, query, **kwargs):
        if len(kwargs) == 0:
            raise Exception("Need to give up args to update!")

        unpacked = self.dialect.unpack(query)

        # remove first table from select
        self.tables_selected = 1

        # make the select 1 due to speedup performances
        sql_information = self.translate_unpacked_query_sql(unpacked)

        if len(sql_information["tables"]) > 1:
            raise RuntimeError("Cannot select more then 1 table in a update statement!")

        # The join statement will start with the first table, the order of these tables should not matter
        # So we just select the first table and join the rest of the tables
        update_vals = ",".join([f"{key}=?" for key in kwargs.keys()])

        return (
            self._update(
                first_table=sql_information["tables"][0],
                update_vals=update_vals,
                where=sql_information["where"],
            ),
            sql_information["args"],
        )

    def delete(self, query):
        unpacked = self.dialect.unpack(query)

        # remove first table from select
        self.tables_selected = 1

        # fields needs to be 1
        sql_information = self.translate_unpacked_query_sql(unpacked)

        if len(sql_information["tables"]) > 1:
            raise RuntimeError("Cannot select more then 1 table in a update statement!")

        # generate sql based on prev calculated vals
        return (
            self._delete(
                first_table=sql_information["tables"][0],
                select=sql_information["where"],
            ),
            sql_information["args"],
        )

    def translate_unpacked_query_sql(
        self, unpacked_query: dict[str, list[str]]
    ) -> dict[str, set | list | str]:
        # all necessary sql information for getting tables, args and the where statement out of the query
        sql_information: dict[str, set | list | str] = {
            "tables": set(),
            "args": [],
            "where_stmt": "",
        }

        # putting unpacked_query[fields, stmts] in its own variable so its more readable
        fields: list[str] = unpacked_query["fields"]
        stmts: list[str] = unpacked_query["stmts"]

        # translates fields to a where stmt so we now what args and tables we need to give up in sql
        def input_field(_field: str, _stmt: str = ""):
            if isinstance(_field, Field):
                _field = str(_field)
                table, field_name = _field.split(".")
                sql_information["tables"].add(table)
                sql_information["where_stmt"] += f" {field_name} {_stmt}"
            else:
                sql_information["args"].append(_field)
                sql_information["where_stmt"] += f" ? {_stmt}"

        # loop until there are no more fields left
        while fields:
            field1: str = fields.pop(0)
            field2: str = fields.pop(0)
            stmt: str = stmts.pop(0)

            input_field(field1, stmt)

            if stmts:
                input_field(field2, stmts.pop(0))
            else:
                input_field(field2)

        # check if there is a where stmt else make the stmt empty
        sql_information["where_stmt"] = (
            f" WHERE {sql_information['where_stmt']}"
            if sql_information["where_stmt"]
            else ""
        )

        # make a list out of the set, we were using a set, so we can't join the same table more than once
        sql_information["tables"] = list(sql_information["tables"])

        return sql_information

    @classmethod
    def field_contains_table(cls, field):
        if not isinstance(field, str):
            return False

        return "." in field

    @classmethod
    def _tables_to_join(cls, tables):
        """
        make it so that every table is joined
        """
        return f"".join([f" INNER JOIN {table}" for table in tables[1:]])

    def insert(self, table_name: str, items: dict):
        return f"INSERT INTO {table_name} ({','.join(items.keys())}) VALUES ({','.join(['?' for _ in items.keys()])})"

    def _select(self, fields, tables, where=None, distinct=None, orderby=None):
        return f"SELECT {distinct}{fields} FROM {tables}{where}{orderby}"

    def _update(self, first_table: str, update_vals: str, where: str):
        return f"UPDATE {first_table} SET {update_vals} {where}"

    def _delete(self, first_table: str, select: str):
        return f"DELETE FROM {first_table} {select}"
