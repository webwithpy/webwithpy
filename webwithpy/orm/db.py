from .objects import Table, Field
from sqlite3 import dbapi2 as sqlite
from pathlib import Path


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class DB:
    conn = None
    cursor = None
    driver = None
    tables = None
    url = None

    def __init__(self, db_path: str):
        driver, db_path = db_path.split(":/")

        if DB.driver is None:
            DB.driver = self._get_driver(driver)

        if DB.conn is None and DB.cursor is None:
            db_path = Path(db_path)

            # make sure the folders to the db and the db itself exists
            db_folder_path = Path(str(db_path)[: -len(str(db_path.name))])
            db_folder_path.mkdir(parents=True, exist_ok=True)
            db_path.touch(exist_ok=True)

            DB.conn = sqlite.connect(db_path)
            DB.conn.row_factory = dict_factory

            DB.conn = DB.conn
            DB.cursor = DB.conn.cursor()
            DB.tables = {}
            DB.url = str(db_path)

    def create_tables(self):
        id_field = Field(field_type="INTEGER PRIMARY KEY AUTOINCREMENT")

        for table in Table.__subclasses__():
            table_name = (
                table.table_name if "table_name" in vars(table) else table.__name__
            )

            table_fields = {
                var: vars(table)[var]
                for var in vars(table)
                if isinstance(vars(table)[var], Field)
            }

            table_fields["id"] = id_field

            for field_name, field in table_fields.items():
                self._set_field(field, field_name, table_name)

            tbl = Table(
                db=self,
                conn=DB.conn,
                cursor=DB.cursor,
                driver=DB.driver,
                table_name=table_name,
                fields=[value for value in table_fields.values()],
            )

            DB.tables[table_name] = tbl
            self._create_table(table_name, *[field for field in table_fields.values()])

    def _set_field(self, field, field_name, table_name):
        field.field_name = field_name
        field.table_name = table_name
        field.cursor = DB.cursor
        field.conn = DB.conn
        field.driver = DB.driver
        field.db = self

    @classmethod
    def _get_driver(cls, driver: str):
        match driver:
            case "sqlite":
                from .drivers.sqlite import SqliteDriver
                from .dialects.sqlite import SqliteDialect

                return SqliteDriver(SqliteDialect)
        raise Exception(f"{driver} is not a valid driver!")

    @classmethod
    def _create_table(cls, table_name: str, *fields: Field):
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        for field in fields:
            sql += f"{field.field_name} {field.field_type}, "
        sql = sql[:-2] + ")"

        DB.cursor.execute(sql)

    def __getattribute__(self, item):
        try:
            return super(DB, self).__getattribute__(item)
        except Exception as e:
            if item in DB.tables.keys():
                return DB.tables[item]
            raise e
