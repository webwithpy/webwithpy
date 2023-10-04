from .dialects.sqlite import SqliteDialect
from .query import Query


class Field:
    def __init__(self, field_name, field_type):
        self.cursor = None
        self.table_name = ""
        self.field_name = field_name
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
        }
        sql_type = field_type_mapping.get(field_type, None)
        if sql_type is None:
            return field_type
        return sql_type

    def __str__(self):
        return f"{self.table_name}.{self.field_name}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return Query(self.cursor, SqliteDialect, SqliteDialect.equals, self, other)

    def __ne__(self, other):
        return Query(self.cursor, SqliteDialect, SqliteDialect.neq, self, other)

    def __lt__(self, other):
        return Query(self.cursor, SqliteDialect, SqliteDialect.lt, self, other)

    def __le__(self, other):
        return Query(self.cursor, SqliteDialect, SqliteDialect.le, self, other)

    def __gt__(self, other):
        return Query(self.cursor, SqliteDialect, SqliteDialect.gt, self, other)

    def __ge__(self, other):
        return Query(self.cursor, SqliteDialect, SqliteDialect.gr, self, other)


class Table:
    def __init__(self, conn=None, db=None, table_name: str = "", fields: list = None):
        self.conn = conn
        self.cursor = db
        self.table_name = table_name
        self.fields: dict = {field.field_name: field for field in fields}

    def __getattribute__(self, item):
        try:
            return super(Table, self).__getattribute__(item)
        except Exception as e:
            if item in self.fields.keys():
                return self.fields[item]

            raise e

    def insert(self, **values):
        return Query(
            conn=self.conn, db=self.cursor, dialect=SqliteDialect, tbl_name=self.table_name
        ).insert(**values, fields=self._get_field_names_sql())

    def select(self, *fields, distinct=False, orderby=None):
        return Query(
            db=self.cursor,
            dialect=SqliteDialect,
            tbl_name=self.table_name,
        ).select(*fields, distinct=distinct, orderby=orderby)

    def _get_field_names(self):
        return [field for field in self.fields if field != "id"]

    def _get_field_names_sql(self):
        return [f'`{field}`' for field in self._get_field_names()]