from ..app import App


class Redirect:
    """
    used for redirecting users to different pages
    """

    def __init__(self, location: str = "/"):
        self.location = location
        App.redirect = self

    def _to_http(self) -> str:
        """
        whenever the user returns a redirect we want to turn it into http
        """
        App.redirect = None
        return (
            f"""HTTP/1.1 301 Moved Permanently\r\nLocation: {self.location}\r\n\r\n"""
        )
