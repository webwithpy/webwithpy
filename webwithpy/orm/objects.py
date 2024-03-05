from .dialects.sqlite import SqliteDialect
from .query import Query
from typing import Dict, Any
import re


class Reference:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end


class DefaultField:
    def __init__(self, cache: bool):
        self.db = None
        self.conn = None
        self.cursor = None
        self.driver = None
        self.table_name = ""
        self.field_name = ""
        self.cache = cache
        self.encrypt: bool = False

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


class Field(DefaultField):
    def __init__(
        self,
        field_type: str = "int",
        field_text: str = "",
        cache: bool = False,
        encrypt: bool = False,
    ):
        """
        :param field_text: Text of the field when it's displayed in for example Html
        :param field_type: Type of the field in sqlite
        :param encrypt: Whether the field is encrypted or not, required for passwords!
        """
        super().__init__(cache)

        self.field_text = field_text
        self.field_type = self._translate_type(field_type)
        self.encrypt = encrypt

    def _translate_type(self, field_type):
        field_type_mapping = {
            "int": "INTEGER",
            "string": "VARCHAR(255)",
            "text": "TEXT",
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


class ReferencedField(DefaultField):
    def __init__(
        self,
        reference: str = "",
        field_text: str = "",
        display_label: str = "",
        cache: bool = False,
    ):
        """
        :param reference: String to referenced field for example 'reference table_name.field_name'. Currently only works
         with ints
        :param field_text: name of the text that will be displayed in grids
        :param display_label: label of the column you want to be displaying, this will make it so that you can display
        different columns in table you are referencing. For example imaging you're referencing id, you can display
        table_name.name instead of table_name.id
        """
        super().__init__(cache)

        reference_data = self._parse_reference(reference)
        self.field_type = reference_data["field_type"]
        self.referenced_table = reference_data["table"]
        self.referenced_field = reference_data["field"]
        self.display_label = display_label
        self.field_text = field_text

    @classmethod
    def _parse_reference(cls, f_reference: str) -> dict[str, str | Any]:
        ref = cls._get_reference_idx(f_reference)
        table, field = f_reference[ref.start + len("reference ") : ref.end].split(".")

        # Using regex to replace the reference string
        pattern = re.compile(r"reference\s+" + re.escape(f"{table}.{field}"))
        f_reference = pattern.sub(f"INTEGER REFERENCES {table}({field})", f_reference)

        return dict(field_type=f_reference, table=table, field=field)

    @classmethod
    def _get_reference_idx(cls, f_reference: str) -> Reference:
        match = re.search(r"reference\s+(\w+\.\w+)", f_reference)
        if match:
            start, end = match.span()
            return Reference(start, end)
        else:
            raise Exception(
                f"{f_reference} table cannot be created due to invalid reference!"
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
        self.table_name = table_name or self.__name__
        self.fields: Dict[str, Field] = {field.field_name: field for field in fields}
        self.dialect = dialect
        self.driver = driver
        self.caching = caching

    def insert(self, **values):
        """
        db.table_name.insert aka inserts data into the db
        """
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
        """
        selects all rows by the table
        """
        return Query(
            db=self.db,
            cursor=self.cursor,
            dialect=self.dialect,
            driver=self.driver,
            tbl_name=self.table_name,
            using_cache=self.caching,
        ).select(*fields, distinct=distinct, orderby=orderby)

    def update(self, **kwargs):
        """
        updates all the fields in the db
        """
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
            # check if the user is getting a function por a variable
            return super(Table, self).__getattribute__(item)
        except Exception as e:
            # if the previous check failed where going to check if the call is equal to a name of an field
            # if yes we want to return that field
            if item in self.fields.keys():
                return self.fields[item]

            # raise if nothing found
            raise e
