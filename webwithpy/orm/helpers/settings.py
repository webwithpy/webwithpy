from pathlib import Path
import os


class DBSettings:
    def __init__(self, uri: str):
        self.uri = uri
        self.db_type = ""
        self.path: Path | str = ""
        self.hostname = ""
        self.username = ""
        self.password = ""
        self.database = ""

        self.parse_uri(uri)
        self.create_path()

    @classmethod
    def _attempt_next_split(cls, s: list[str], sep: str) -> list[str]:
        if len(s) > 1:
            return s[1].split(sep, maxsplit=1)

        return [""]

    def parse_uri(self, uri: str):
        uri_split = uri.split(":/")
        path_split = self._attempt_next_split(uri_split, "|")
        username_split = self._attempt_next_split(path_split, ":")
        password_split = self._attempt_next_split(username_split, "@")
        hostname_db_split = self._attempt_next_split(password_split, "/")

        self.db_type = uri_split[0]
        self.path = Path(f"{os.getcwd()}/{path_split[0]}")
        self.username = username_split[0]
        self.password = password_split[0]
        self.hostname = hostname_db_split[0]
        self.database = hostname_db_split[1] if len(hostname_db_split) > 1 else ""

    def create_path(self):
        db_folder_path = Path(str(self.path)[: -len(str(self.path.name))])
        db_folder_path.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.touch(exist_ok=True)
