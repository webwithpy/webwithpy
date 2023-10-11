from numba import njit


class Query:
    def __init__(
        self,
        *,
        conn=None,
        cursor=None,
        dialect=None,
        operator="=",
        first=None,
        second=None,
        tbl_name: str = None,
    ):
        self.conn = conn
        self.cursor = cursor
        self.dialect = dialect
        self.operator = operator
        self.first = first
        self.second = second
        self.table_name = tbl_name
        # removes the amount of table from the select bc they are already selected
        self.tables_selected = 0

    def insert(self, fields=None, **values) -> None:
        """
        NOTE ALL FIELDS ARE REQUIRED TO USE THE INSERT CURRENTLY
        :param values: list of values that will be inserted into the table
        :param fields: all name of fields that the table has excluding the id field
        :return:
        """
        if fields is None:
            fields = self.cursor.tables[self.table_name].fields.keys()

        sql = self._insert(fields=fields, values=values)
        self.cursor.execute(sql)
        self.conn.commit()

    def _select_gen_sql(self, *fields: tuple | int, distinct=False, orderby=None):
        # if no fields are specified, select all fields
        fields = [str(field) for field in fields] if len(fields) != 0 else "*"

        # unpack the query into a dict, note that the query uses a tree structure.
        # So a query can have a query as a child, which can have a query as a child, etc.
        # This unpacks the tree structure into a list of fields and a list of statements
        unpacked = self.dialect.unpack(self)
        if unpacked["fields"][0] is None:
            tables, where = self._unpacked_as_sql(unpacked).values()
            # where not doing a where stmt here!
            where = ""
        else:
            tables, where = self._unpacked_as_sql(unpacked).values()

        # if no table is found by unpacking the query, use the table_name specified in the select method
        # this is due to the user not using a where query and only db.table.select()
        tables = tables[self.tables_selected : :]
        if len(tables) == 0:
            tables.append(self.table_name)

        # the join statement will start with the first table, the order of these tables should not matter
        # so we just select the first table and join the rest of the tables
        join = f"{tables[0]} "

        # however we can only join the tables if there are more then 1 table
        if len(tables) > 1:
            join += self._tbls_to_join(tables)

        # if there is a where statement, add it to the join statement
        fields = ", ".join(fields) if isinstance(fields, list) else fields
        distinct = "DISTINCT " if distinct else ""
        orderby = f"ORDER BY {orderby}" if orderby else ""

        return self._select(
            fields=fields, tables=join, where=where, distinct=distinct, orderby=orderby
        )

    def select(self, *fields: tuple, distinct=False, orderby=None) -> list[dict]:
        """
        Selects fields from the database and returns the result as a list of dicts
        :param fields: list of fields you want to select from the database
        :param distinct: use if you only want 1 of any value
        :param orderby: orders the result by the specified field
        :return:
        """

        # generate the select statement from what we have generated above
        sql = self._select_gen_sql(*fields, distinct=distinct, orderby=orderby)

        return self.cursor.execute(sql).fetchall()

    def update(self, **values):
        unpacked = self.dialect.unpack(self)

        # remove first table from select
        self.tables_selected = 1

        # make the select 1 due to speedup performances
        select = self._select_gen_sql(1, distinct=False, orderby="")
        tables, where = self._unpacked_as_sql(unpacked).values()

        # The join statement will start with the first table, the order of these tables should not matter
        # So we just select the first table and join the rest of the tables
        update_vals = self._set(values)
        sql = self._update(
            first_table=tables[0], update_vals=update_vals, select=select
        )

        self.cursor.execute(sql)
        self.conn.commit()

    def delete(self):
        unpacked = self.dialect.unpack(self)

        # remove first table from select
        self.tables_selected = 1

        # fields needs to be 1
        select = self._select_gen_sql(1, distinct=False, orderby="")
        tables, where = self._unpacked_as_sql(unpacked).values()

        # generate sql based on prev calculated vals
        sql = self._delete(first_table=tables[0], select=select)

        self.cursor.execute(sql)
        self.conn.commit()

    def _update(self, first_table: str, update_vals: str, select: str):
        return f"UPDATE {first_table} SET {update_vals} WHERE EXISTS ({select})"

    def _insert(self, fields, values):
        return f"INSERT INTO {self.table_name} ({', '.join(fields)}) VALUES ({', '.join([str(val) for val in values.values()])})"

    def _select(self, fields, tables, where=None, distinct=None, orderby=None):
        return f"SELECT {distinct}{fields} FROM {tables}{where}{orderby}"

    def _delete(self, first_table: str, select: str):
        return f"DELETE FROM {first_table} WHERE EXISTS ({select})"

    def _tbls_to_join(self, tables):
        sql = f""
        for table in tables[1:]:
            sql += f" INNER JOIN {table} "
        return sql

    def _unpacked_as_sql(self, unpacked: dict):
        sql = {"tables": [], "where": " WHERE "}

        while unpacked["fields"]:
            field1 = str(unpacked["fields"].pop(0))
            field2 = str(unpacked["fields"].pop(0))
            stmt = unpacked["stmts"].pop(0)

            sql["where"] += (tl := self._translate_field(field1))["where"]

            if tl["table"] and tl["table"] not in sql["tables"]:
                sql["tables"].append(tl["table"])

            sql["where"] += f"{stmt} {(tl := self._translate_field(field2))['where']}"

            if tl["table"] and tl["table"] not in sql["tables"]:
                sql["tables"].append(tl["table"])

            if unpacked["stmts"]:
                sql["where"] += unpacked["stmts"].pop(0) + " "

        return sql

    def _translate_field(self, field):
        if "." in str(field):
            table = field.split(".")[0]
            where = f"{field} "
        elif str(field).replace("-", "").isdigit():
            table = None
            where = f"{field} "
        else:
            table = None
            where = f"'{field}' "

        return dict(table=table, where=where)

    @njit
    def _set(self, values: dict):
        sql = ""
        first_done = False
        for key, value in values.items():
            if first_done:
                sql += ", "
            if str(value).isdigit():
                sql += f"{key} = {value} "
            else:
                sql += f"{key} = {value} "
            first_done = True
        return sql

    def __and__(self, other):
        return Query(
            conn=self.conn,
            cursor=self.cursor,
            dialect=self.dialect,
            operator=self.dialect.and_,
            first=self,
            second=other,
        )

    def __or__(self, other):
        return Query(
            conn=self.conn,
            cursor=self.cursor,
            dialect=self.dialect,
            operator=self.dialect.or_,
            first=self,
            second=other,
        )
