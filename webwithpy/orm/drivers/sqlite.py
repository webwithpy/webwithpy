class SqliteDriver:
    def __init__(self, dialect):
        self.dialect = dialect

        # removes the amount of table from the select bc they are already selected
        self.tables_selected = 0

    def update(self, query, **kwargs):
        if len(kwargs) == 0:
            raise Exception("Need to give up args to update!")

        unpacked = self.dialect.unpack(query)

        # remove first table from select
        self.tables_selected = 1

        # make the select 1 due to speedup performances
        tables, where = self._unpacked_as_sql(unpacked).values()

        if len(tables) > 1:
            raise RuntimeError("Cannot select more then 1 table in a update statement!")

        # The join statement will start with the first table, the order of these tables should not matter
        # So we just select the first table and join the rest of the tables
        update_vals = ",".join([f"{key}=?" for key in kwargs.keys()])

        return self._update(first_table=tables[0], update_vals=update_vals, where=where)

    def delete(self, query):
        unpacked = self.dialect.unpack(query)

        # remove first table from select
        self.tables_selected = 1

        # fields needs to be 1
        tables, where = self._unpacked_as_sql(unpacked).values()

        if len(tables) > 1:
            raise RuntimeError("Cannot select more then 1 table in a update statement!")

        # generate sql based on prev calculated vals
        return self._delete(first_table=tables[0], select=where)

    def select_sql(
        self,
        *fields: tuple | int,
        query=None,
        table_name=None,
        distinct=False,
        orderby=None,
    ):
        # if no fields are specified, select all fields
        fields = [str(field) for field in fields] if len(fields) != 0 else "*"

        # unpack the query into a dict, note that the query uses a tree structure.
        # So a query can have a query as a child, which can have a query as a child, etc.
        # This unpacks the tree structure into a list of fields and a list of statements
        unpacked = self.dialect.unpack(query)
        if unpacked["fields"][0] is None:
            tables, where = self._unpacked_as_sql(unpacked).values()
            # were not doing a where stmt here!
            where = ""
        else:
            tables, where = self._unpacked_as_sql(unpacked).values()

        # if no table is found by unpacking the query, use the table_name specified in the select method
        # this is due to the user not using a where query and only db.table.select()
        tables = tables[self.tables_selected : :]

        # the join statement will start with the first table, the order of these tables should not matter
        # so we just select the first table and join the rest of the tables
        if len(tables) != 0:
            join = f"{tables[0]} "
        else:
            join = f"{table_name} {table_name}"
            where = where.replace(table_name, f"{table_name}")

        # however we can only join the tables if there are more then 1 table
        if len(tables) > 1:
            join += self._tables_to_join(tables)

        # if there is a where statement, add it to the join statement
        fields = ", ".join(fields) if isinstance(fields, list) else fields
        distinct = "DISTINCT " if distinct else ""
        orderby = f"ORDER BY {orderby}" if orderby else ""

        return self._select(
            fields=fields, tables=join, where=where, distinct=distinct, orderby=orderby
        )

    @classmethod
    def _tables_to_join(cls, tables):
        """
        make it so that every table is joined
        """
        return f"".join([f" INNER JOIN {table}" for table in tables[1:]])

    def _unpacked_as_sql(self, unpacked: dict) -> dict:
        sql = {"tables": [], "where": " WHERE "}

        while unpacked["fields"]:
            # grab 2 fields and a stmt to make an expr in the future
            field1 = str(unpacked["fields"].pop(0))
            field2 = str(unpacked["fields"].pop(0))
            stmt = unpacked["stmts"].pop(0)

            field_sql_dict = self.field_to_sql_dict(field1, sql["tables"])
            sql["where"] += field_sql_dict["field"]

            if field_sql_dict["table"] is not None:
                sql["tables"].append(field_sql_dict["table"])

            field_sql_dict = self.field_to_sql_dict(field2, sql["tables"])
            sql["where"] += f"{stmt} {field_sql_dict['field']}"

            if field_sql_dict["table"] is not None:
                sql["tables"].append(field_sql_dict["table"])

            if unpacked["stmts"]:
                sql["where"] += unpacked["stmts"].pop(0) + " "

        return sql

    @classmethod
    def field_to_sql_dict(cls, field: str, sql_tables: list):
        translated_field = cls._translate_field(field)
        table = (
            translated_field["table"]
            if translated_field["table"] and translated_field["table"] not in sql_tables
            else None
        )

        return dict(field=translated_field["field"], table=table)

    @classmethod
    def _translate_field(cls, field):
        if "." in str(field):
            table = field.split(".")[0]
            field = f"{field} "
        elif str(field).replace("-", "").isdigit():
            table = None
            field = f"{field} "
        else:
            table = None
            field = f"'{field}' "

        return dict(table=table, field=field)

    @classmethod
    def _set(cls, values: dict[str, str | bytes]):
        """
        turns a set of values into a key = value statement.
        example -> {"a": 2} returns "a=2"
        example2 -> {"a": 2, "b": "hi"} returns "a=2, b='hi'"
        """
        sql = ""
        first_done = False
        for key, value in values.items():
            if key == "id":
                continue

            if first_done:
                sql += ", "
            if str(value).isdigit():
                sql += f"{key} = {value} "
            else:
                sql += f"{key} = '{value}'"

            first_done = True
        return sql

    def to_cache_keys(self, query):
        unpacked = self.dialect.unpack(query)
        if unpacked["fields"][0] is None:
            tables, where = self._unpacked_as_sql(unpacked).values()
            # were not doing a where stmt here!
            where = ""
        else:
            tables, where = self._unpacked_as_sql(unpacked).values()

        return "".join(tables) + where

    def insert(self, table_name: str, items: dict):
        return f"INSERT INTO {table_name} ({','.join(items.keys())}) VALUES ({','.join(['?' for _ in items.keys()])})"

    def _select(self, fields, tables, where=None, distinct=None, orderby=None):
        return f"SELECT {distinct}{fields} FROM {tables}{where}{orderby}"

    def _update(self, first_table: str, update_vals: str, where: str):
        return f"UPDATE {first_table} SET {update_vals} {where}"

    def _delete(self, first_table: str, select: str):
        return f"DELETE FROM {first_table} {select}"
