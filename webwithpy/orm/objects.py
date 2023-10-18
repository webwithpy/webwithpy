from .dialects.sqlite import SqliteDialect
from .query import Query


class Field:
    def __init__(self, field_type):
        self.db = None
        self.conn = None
        self.cursor = None
        self.driver = None
        self.table_name = ""
        self.field_name = ""
        self.field_type = self._translate_type(field_type)

    def _translate_type(self, field_type):
        field_type_mapping = {
            "int": "INTEGER",
            "string": "VARCHAR(255)",
            "float": "FLOAT",
            "bool": "BOOLEAN",
            "date": "DATE",
            "datetime": "DATETIME",
            "time": "TIME",
            "image": "IMAGE"
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
        )


class Table:
    def __init__(self, db=None, conn=None, cursor=None, table_name: str = "", fields: list = None, dialect=None, driver=None):
        self.db = db
        self.conn = conn
        self.cursor = cursor
        self.table_name = table_name
        self.fields: dict = {field.field_name: field for field in fields}
        self.dialect = dialect
        self.driver = driver

    def insert(self, **values):
        return Query(
            db=self.db,
            conn=self.conn,
            cursor=self.cursor,
            dialect=SqliteDialect,
            driver=self.driver,
            tbl_name=self.table_name,
        ).insert(**values, fields=self._get_field_names_sql())

    def select(self, *fields, distinct=False, orderby=None):
        return Query(
            db=self.db,
            cursor=self.cursor,
            dialect=self.dialect,
            driver=self.driver,
            tbl_name=self.table_name,
        ).select(*fields, distinct=distinct, orderby=orderby)

    def update(self, **kwargs):
        return Query(
            db=self.db,
            cursor=self.cursor,
            dialect=self.dialect,
            driver=self.driver,
            tbl_name=self.table_name,
        ).update(**kwargs)

    def _get_field_names(self):
        return [field for field in self.fields if field != "id"]

    def _get_field_names_sql(self):
        return [f"`{field}`" for field in self._get_field_names()]

    def __getattribute__(self, item):
        try:
            return super(Table, self).__getattribute__(item)
        except Exception as e:
            if item in self.fields.keys():
                return self.fields[item]

            raise e
