from webwithpy.orm.dialects.mysql import MysqlDialect
from typing import Type


class MysqlDriver:
    def __init__(self, dialect: Type[MysqlDialect]):
        self.dialect = dialect
