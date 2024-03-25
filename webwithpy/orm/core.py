from __future__ import annotations
from .helpers.settings import DBSettings
from typing import TYPE_CHECKING, Type
from .objects.objects import Table, ReferencedField, Field, DefaultField

if TYPE_CHECKING:
    from .dialect.base import IDialect
    from .drivers.driver import IDriver


class DB:
    tables: dict[str, Table] = None
    dialect: IDialect = None
    driver: IDriver = None
    _settings: DBSettings = None

    def __init__(self, uri: str):
        DB._settings = DBSettings(uri)
        self._settings = DB._settings

        self._init_driver(self._settings.db_type)
        if not DB.tables:
            DB.tables = {}

    def create_table(self, table: Type[Table]):
        id_field = Field(DB.dialect.primary_key())

        # setup all fields of the table
        table_fields = {
            var: vars(table)[var]
            for var in vars(table)
            if isinstance(vars(table)[var], Field)
        }

        caching = False
        table_name = table.table_name if "table_name" in vars(table) else table.__name__
        table_fields["id"] = id_field

        for field_name, field in table_fields.items():
            if "reference" in field.field_type:
                table_fields[field_name] = ReferencedField(
                    field.field_type, field.field_text, field.cache
                )
            if field.cache:
                caching = True

        for field_name, field in table_fields.items():
            self._set_field(
                field=field, field_name=field_name, table_name=table_name, cache=caching
            )

        tbl = Table(
            driver=DB.driver,
            name=table_name,
            caching=caching,
            fields=[value for value in table_fields.values()],
        )

        DB.tables[table_name] = tbl
        self._create_table(table_name, [field for field in table_fields.values()])

    def create_tables(self, *tables: Type[Table]):
        for table in tables:
            self.create_table(table)

    @classmethod
    def _set_field(
        cls, field: DefaultField, field_name: str, table_name: str, cache: bool
    ):
        """
        sets the appropriate fields for the Field class
        """
        field.name = field_name
        field.table_name = table_name
        field.driver = DB.driver
        field.cache = cache

    @classmethod
    def _create_table(cls, table_name: str, fields: list[Field]):
        sql = DB.dialect.create_table(table_name=table_name, fields=fields)
        DB.driver.execute_sql(sql)

    def _init_driver(self, driver_name: str):
        match driver_name:
            case "sqlite":
                from .drivers.sqlite import SqliteDriver
                from .dialect.sqlite import SqliteDialect

                DB.driver = SqliteDriver(self._settings)
                DB.dialect = SqliteDialect()
            case "mysql":
                from .drivers.mysql import MysqlDriver
                from .dialect.mysql import MysqlDialect

                DB.driver = MysqlDriver(self._settings)
                DB.dialect = MysqlDialect()
            case _:
                raise ValueError(f"could not find driver {driver_name}")

    def __getattribute__(self, item):
        try:
            return super(DB, self).__getattribute__(item)
        except AttributeError as e:
            if isinstance(item, str):
                if item in DB.tables:
                    return DB.tables.get(item)

            raise e
