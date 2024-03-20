from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..drivers.driver import IDriver
from .query import Query

import re

if TYPE_CHECKING:
    from ..dialect.base import IDialect


class Reference:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end


class Table:
    def __init__(
        self, driver: IDriver, name: str, caching: bool = False, fields: list = None
    ):
        self.driver = driver
        self.table_name = name
        self.fields: list = fields or []
        self.caching = caching

    def get_field(self, name: str) -> DefaultField | None:
        for field in self.fields:
            if field.name == name:
                return field

        return None

    def insert(self, **items: Any):
        self.driver.insert(self, items)

    def select(self):
        # here we create a sql statement that is always true, so we can select all fields.
        # this is necessary since driver.select expects a query
        self.driver.select(
            Query(self.driver, self.fields[0], 0, "=")
            | Query(self.driver, self.fields, 0, "!="),
        )

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError as e:
            if not isinstance(item, str):
                raise e

            for field in self.fields:
                if field.name == item:
                    return field

            raise e


class DefaultField:
    def __init__(
        self,
        field_type: str,
        field_text: str = "",
        cache: bool = False,
        encrypt: bool = False,
    ):
        self.field_type = self._translate_type(field_type)
        self.field_text = field_text
        self.table_name = ""
        self.encrypt = encrypt
        self.driver = None
        self.cache = cache
        self.name = ""

    @classmethod
    def _translate_type(cls, field_type):
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

    def __eq__(self, other):
        return Query(self.driver, self, other, "=")

    def __ge__(self, other):
        return Query(self.driver, self, other, ">=")

    def __le__(self, other):
        return Query(self.driver, self, other, "<=")

    def __lt__(self, other):
        return Query(self.driver, self, other, "<")

    def __gt__(self, other):
        return Query(self.driver, self, other, ">")

    def __str__(self):
        return f"{self.table_name}.{self.name}"


class ReferencedField(DefaultField):
    def __init__(
        self,
        reference: str = "",
        field_text: str = "",
        display_label: str = "",
        cache: bool = False,
        encrypt: bool = False,
    ):
        """
        :param reference: String to referenced field for example 'reference table_name.field_name'. Currently only works
         with ints
        :param field_text: name of the text that will be displayed in grids
        :param display_label: label of the column you want to be displaying, this will make it so that you can display
        different columns in table you are referencing. For example imaging you're referencing id, you can display
        table_name.name instead of table_name.id
        """
        reference_data = self._parse_reference(reference)
        self.field_type = reference_data["field_type"]
        self.referenced_table = reference_data["table"]
        self.referenced_field = reference_data["field"]
        self.display_label = display_label
        self.field_text = field_text

        super().__init__(
            field_type=self.field_type,
            field_text=self.field_text,
            cache=cache,
            encrypt=encrypt,
        )

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


class Field(DefaultField):
    pass
