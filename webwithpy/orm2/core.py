from .helpers.uri_helper import Uri


class DB:
    driver = None

    def __init__(self, uri: str):
        self._uri = uri
        self._init_driver(Uri.get_db_name(uri))

    @classmethod
    def _init_driver(cls, driver_name: str):
        match driver_name:
            case "sqlite":
                ...
            case "mysql":
                ...
            case _:
                raise ValueError(f"could not find driver {driver_name}")
