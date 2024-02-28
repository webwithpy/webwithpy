from __future__ import annotations
from .tools import cacher
import bcrypt

# Add everything for type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drivers.driver_interface import IDriver
    from ..orm.db import DB


class Query:
    def __init__(
        self,
        *,
        db=None,
        conn=None,
        cursor=None,
        dialect=None,
        driver: IDriver = None,
        operator="=",
        first=None,
        second=None,
        tbl_name: str = None,
        using_cache: bool = False,
    ):
        self.db: DB = db
        self.conn = conn
        self.cursor = cursor
        self.dialect = dialect
        self.driver: IDriver = driver
        self.operator = operator
        self.first = first
        self.second = second
        self.table_name = tbl_name
        self.using_cache = using_cache

    def __tables__(self):
        unpacked_query = self.dialect.unpack(self)
        return self.driver.translate_unpacked_query_sql(unpacked_query).get(
            "tables"
        ) or {self.table_name: self.db.tables[self.table_name]}

    def insert(self, **kwargs) -> None:
        """
        :param kwargs: list of values that will be inserted into the table
        :return:
        """
        sql = self.driver.insert(table_name=self.table_name, items=kwargs)

        for field in self.__tables__()[self.table_name].fields.values():
            if field.encrypt:
                kwargs[field.field_name] = bcrypt.hashpw(
                    password=kwargs[field.field_name].encode(),
                    salt=bcrypt.gensalt(rounds=8),
                )

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
        # generate the select statement
        sql, args = self.driver.select_sql(
            *fields,
            table_name=self.table_name,
            query=self,
            distinct=distinct,
            orderby=orderby,
        )

        # caching logic
        if self.using_cache:
            if cached := cacher.get_cache_by_select(
                table_name=self.table_name, select_stmt=sql
            ):
                return cached
            else:
                value = self.cursor.execute(sql, args).fetchall()
                cacher.insert_cache(
                    table_name=self.table_name, select_stmt=sql, value=value
                )

                return value

        # execute the sql
        return self.cursor.execute(sql, args).fetchall()

    def update(self, **kwargs):
        # remove table from cache if we are caching tables
        if self.using_cache:
            cacher.remove_table_cache(self.table_name)

        # get update statement and args from query
        sql, args = self.driver.update(query=self, **kwargs)

        self.cursor.execute(sql, list(kwargs.values()) + args)
        self.conn.commit()

    def delete(self):
        # remove table from cache if we are caching tables
        if self.using_cache:
            cacher.remove_table_cache(self.table_name)

        # get delete statement from driver
        sql, args = self.driver.delete(query=self)

        # execute sql
        self.cursor.execute(sql, args)
        self.conn.commit()

    def __and__(self, other):
        # make it so we can use logic on queries
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=self.dialect,
            operator=self.dialect.and_,
            driver=self.driver,
            first=self,
            second=other,
            using_cache=self.using_cache,
        )

    def __or__(self, other):
        # make it so we can use logic on queries
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=self.dialect,
            operator=self.dialect.or_,
            driver=self.driver,
            first=self,
            second=other,
            using_cache=self.using_cache,
        )
