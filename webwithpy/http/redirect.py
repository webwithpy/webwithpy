from ..app import App


class Redirect:
    def __init__(self, location: str = "/"):
        self.location = location
        App.redirect = self

    def _to_http(self):
        App.redirect = None
        return (
            f"""HTTP/1.1 301 Moved Permanently\r\nLocation: {self.location}\r\n\r\n"""
        )
