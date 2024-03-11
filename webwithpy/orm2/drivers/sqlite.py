from ..drivers.driver import DefaultDriver
from ..helpers.db_settings import DBSettings
from sqlite3 import dbapi2 as sqlite


class SqliteDriver(DefaultDriver):
    def __init__(self, db_settings: DBSettings) -> None:
        super().__init__(db_settings)

    def connect(self) -> None:
        self.conn = sqlite.connect(self.settings.path, timeout=10)

    def execute_sql(self, sql: str):
        if self.conn:
            self.conn.execute(sql)

        raise ValueError("Connection isn't initialized to the database")
