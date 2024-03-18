from typing import Any

from ..drivers.driver import IDriver
from .query import Query


class Table:
    def __init__(
        self, driver: IDriver, name: str, caching: bool = False, fields: list = None
    ):
        self.driver = driver
        self.table_name = name
        self.fields: list = fields or []
        self.caching = caching

    def get_field(self, name: str):
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
        self.field_type = field_type
        self.field_text = field_text
        self.table_name = ""
        self.encrypt = encrypt
        self.driver = None
        self.cache = cache
        self.name = ""

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
    pass


class Field(DefaultField):
    pass
