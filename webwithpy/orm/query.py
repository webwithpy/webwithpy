class Query:
    def __init__(
        self,
        *,
        db=None,
        conn=None,
        cursor=None,
        dialect=None,
        driver=None,
        operator="=",
        first=None,
        second=None,
        tbl_name: str = None,
    ):
        self.db = db
        self.conn = conn
        self.cursor = cursor
        self.dialect = dialect
        self.driver = driver
        self.operator = operator
        self.first = first
        self.second = second
        self.table_name = tbl_name

    def __tables__(self):
        unpacked_query = self.dialect.unpack(self)
        return self.driver._unpacked_as_sql(unpacked_query)["tables"]

    def insert(self, **kwargs) -> None:
        """
        NOTE ALL FIELDS ARE REQUIRED TO USE THE INSERT CURRENTLY
        :param kwargs: list of values that will be inserted into the table
        :return:
        """
        sql = self.driver.insert(table_name=self.table_name, items=kwargs)

        self.cursor.execute(sql, tuple(kwargs.values()))
        self.conn.commit()

    def select(self, *fields: tuple, distinct=False, orderby=None) -> list[dict]:
        """
        Selects fields from the database and returns the result as a list of dicts
        :param fields: list of fields you want to select from the database
        :param distinct: use if you only want 1 of any value
        :param orderby: orders the result by the specified field
        :return:
        """

        # generate the select statement from what we have generated above
        sql = self.driver.select_sql(
            *fields,
            table_name=self.table_name,
            query=self,
            distinct=distinct,
            orderby=orderby,
        )

        return self.cursor.execute(sql).fetchall()

    def update(self, **kwargs):
        sql = self.driver.update(query=self, **kwargs)

        self.cursor.execute(sql, tuple(kwargs.values()))
        self.conn.commit()

    def delete(self):
        sql = self.driver.delete(query=self)

        self.cursor.execute(sql)
        self.conn.commit()

    def __and__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=self.dialect,
            operator=self.dialect.and_,
            driver=self.driver,
            first=self,
            second=other,
        )

    def __or__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=self.dialect,
            operator=self.dialect.or_,
            driver=self.driver,
            first=self,
            second=other,
        )
