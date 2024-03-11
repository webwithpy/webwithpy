from ..helpers.uri_helper import Uri


class DBSettings(object):
    def __init__(self, uri: str, pool_size: int = 0, attempts: int = 3):
        self.pool_size = pool_size
        self.attempts = attempts
        self.path = Uri.get_db_path(uri)
