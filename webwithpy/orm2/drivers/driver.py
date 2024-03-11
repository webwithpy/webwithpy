from ..helpers.db_settings import DBSettings


class DefaultDriver:
    def __init__(self, settings: DBSettings) -> None:
        self.settings = settings
        self.conn = None

    def connect(self): ...

    def setup(self): ...

    def execute_sql(self, sql: str): ...
