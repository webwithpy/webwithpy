from .dialects.sqlite import SqliteDialect
from .query import Query
from typing import Dict


class Field:
    def __init__(self, field_type, encrypt: bool = False):
        self.db = None
        self.conn = None
        self.cursor = None
        self.driver = None
        self.table_name = ""
        self.field_name = ""
        self.field_type = self._translate_type(field_type)
        self.cache = False
        self.encrypt = encrypt

    def _translate_type(self, field_type):
        field_type_mapping = {
            "int": "INTEGER",
            "string": "VARCHAR(255)",
            "float": "FLOAT",
            "bool": "BOOLEAN",
            "date": "DATE",
            "datetime": "DATETIME",
            "time": "TIME",
            "image": "IMAGE",
        }
        sql_type = field_type_mapping.get(field_type.lower(), None)
        if sql_type is None:
            return field_type
        return sql_type

    def __str__(self):
        return f"{self.table_name}.{self.field_name}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            operator=SqliteDialect.equals,
            tbl_name=self.table_name,
            driver=self.driver,
            first=self,
            second=other,
            using_cache=self.cache,
        )

    def __ne__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            operator=SqliteDialect.neq,
            driver=self.driver,
            first=self,
            second=other,
            tbl_name=self.table_name,
            using_cache=self.cache,
        )

    def __lt__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            operator=SqliteDialect.lt,
            driver=self.driver,
            first=self,
            second=other,
            tbl_name=self.table_name,
            using_cache=self.cache,
        )

    def __le__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            operator=SqliteDialect.le,
            driver=self.driver,
            first=self,
            second=other,
            tbl_name=self.table_name,
            using_cache=self.cache,
        )

    def __gt__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            operator=SqliteDialect.gt,
            driver=self.driver,
            first=self,
            second=other,
            tbl_name=self.table_name,
            using_cache=self.cache,
        )

    def __ge__(self, other):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            operator=SqliteDialect.ge,
            driver=self.driver,
            first=self,
            second=other,
            tbl_name=self.table_name,
            using_cache=self.cache,
        )


class Table:
    def __init__(
        self,
        db=None,
        conn=None,
        caching=False,
        cursor=None,
        table_name: str = "",
        fields: list = None,
        dialect=None,
        driver=None,
    ):
        self.db = db
        self.conn = conn
        self.cursor = cursor
        self.table_name = table_name
        self.fields: Dict[str, Field] = {field.field_name: field for field in fields}
        self.dialect = dialect
        self.driver = driver
        self.caching = caching

    def insert(self, **values):
        Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            driver=self.driver,
            tbl_name=self.table_name,
            using_cache=self.caching,
        ).insert(**values)

    def select(self, *fields, distinct=False, orderby=None):
        return Query(
            db=self.db,
            cursor=self.cursor,
            dialect=self.dialect,
            driver=self.driver,
            tbl_name=self.table_name,
            using_cache=self.caching,
        ).select(*fields, distinct=distinct, orderby=orderby)

    def update(self, **kwargs):
        return Query(
            db=self.db,
            cursor=self.cursor,
            dialect=self.dialect,
            driver=self.driver,
            tbl_name=self.table_name,
            using_cache=self.caching,
        ).update(**kwargs)

    def __getattribute__(self, item):
        try:
            return super(Table, self).__getattribute__(item)
        except Exception as e:
            if item in self.fields.keys():
                return self.fields[item]

            raise e
