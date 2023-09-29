from .helpers.SQLHelper import SqlHelper as SQLHelper
from sqlite3 import Connection
from typing import List, Union


class Field:
    def __init__(self, field_name: str, field_type: str):
        self.name = field_name
        self.type = field_type
        self.table_name = ""
        self.conn: Connection = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}: {self.type}"

    def __getattribute__(self, item):
        try:
            return super(Field, self).__getattribute__(item)
        except AttributeError as e:
            raise Exception("Not implemented")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return SQLHelper.get_fields_by_tbl(self.conn, self.table_name, '=', self.name, other)

    def __ge__(self, other):
        return SQLHelper.get_fields_by_tbl(self.conn, self.table_name, '>=', self.name, other)

    def __gt__(self, other):
        return SQLHelper.get_fields_by_tbl(self.conn, self.table_name, '>', self.name, other)

    def __lt__(self, other):
        return SQLHelper.get_fields_by_tbl(self.conn, self.table_name, '<', self.name, other)

    def __le__(self, other):
        return SQLHelper.get_fields_by_tbl(self.conn, self.table_name, '<=', self.name, other)


class Table:
    def __init__(self, name: str, fields: List[Field], migrate: bool):
        self.name = name
        self.fields: List[Field] = fields or []
        self.migrate = migrate

    def __getattribute__(self, item):
        try:
            return super(Table, self).__getattribute__(item)
        except AttributeError as e:
            for field in self.fields:
                if field.name == item:
                    return field
            raise e

    # def __hash__(self):
    #     return hash(self.name)
