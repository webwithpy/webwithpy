from functools import wraps
import time
from pydal import DAL


class DB(DAL, object):
    """based on pydal with a async -> sync layer above it"""
    def __init__(
        self,
        uri="sqlite://dummy.db",
        pool_size=0,
        folder=None,
        db_codec="UTF-8",
        check_reserved=None,
        migrate=True,
        fake_migrate=False,
        migrate_enabled=True,
        fake_migrate_all=False,
        decode_credentials=False,
        driver_args=None,
        adapter_args=None,
        attempts=5,
        auto_import=False,
        bigint_id=False,
        debug=False,
        lazy_tables=False,
        db_uid=None,
        after_connection=None,
        tables=None,
        ignore_field_case=True,
        entity_quoting=True,
        table_hash=None,
    ):

        self.locked = False

    def interceptor(self, function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                while self.locked:
                    continue

                self.locked = True
                return function(*args, **kwargs)
            finally:
                self.locked = False

        return wrapper

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)
        if hasattr(attr, "__call__") and item not in ["interceptor", "locked"]:
            return self.interceptor(attr)
        else:
            return attr
