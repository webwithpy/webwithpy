from typing import Dict, Any


class CookieJar:
    def __init__(self):
        self.cookies: Dict[str, Any] = {}

    def get_http_cookies(self) -> str:
        """
        sets up the cookies to be sent over http(not encoded!). All cookies are currently Secure and go away after 1 day
        """
        response = ""

        for name, value in self.cookies.items():
            response += f"Set-Cookie: {name}={value}; Max-Age: 86400; SameSite=Strict\n"

        return response

    def add_cookie(self, name: str, value: Any):
        if isinstance(value, str):
            value = value.replace("\r", "")

        self.cookies[name] = value

    def remove_cookie(self, name: str):
        del self.cookies[name]

    def get_cookie(self, name: str):
        return self.cookies.get(name)
