from typing import Union, Any
from os import PathLike

from .cookies import CookieJar
from ..html.lexer import Lexer
from ..html.parser import DefaultParser
from ..html.renderer import DefaultRenderer


class Response:
    def __init__(self, session):
        # default headers for the response
        self.http_version: str = "1.1"
        self.content_type: str = "text/html"

        # necessary headers
        self.headers = {
            "Cache-Control": "max-age=0, no-cache, must-revalidate, proxy-revalidate",
        }

        self.contents = []

        # cached templates for faster loading times and less server stress
        self._cache = {}

        # Make sure we create the cookie jar and always include the user's session
        # _ means the variable is 'private'(private vars don't exist however they do in code editors like pycharm!)
        self._cookie_jar = CookieJar()
        self._cookie_jar.add_cookie("session", session)
        self.error = None

    def get_all_cookies(self):
        """
        Get all cookies from the cookie jar
        """
        return self._cookie_jar.cookies.items()

    def get_cookie(self, name: str) -> Any:
        """
        Get a cookie from the cookie jar
        """
        return self._cookie_jar.get_cookie(name)

    def remove_cookie(self, name: str):
        """
        Remove a cookie from the cookie jar, so it won't be used in the http request
        """
        self._cookie_jar.remove_cookie(name)

    def add_cookie(self, cookie_name: str, cookie_value):
        """Exposes the cookie jar add_cookie method so users can use it"""
        self._cookie_jar.add_cookie(cookie_name, cookie_value)

    def _add_content(self, content: Any, template: Union[str, PathLike] = ""):
        """
        function will add any content given the user based on if he gave-up a template
        """
        if template is not None and template != "":
            if not isinstance(content, dict):
                content = {"result": content}

            rendered = (
                self._parse_template(template, **content)
                if template not in self._cache
                else DefaultRenderer.render_pre(self._cache[template], **content)
            )
            self.contents.append(rendered)
        else:
            self.contents.append(str(content))

    def _parse_template(self, template: Union[str, PathLike], **kwargs):
        """
        Parses the given template with htpyp
        """
        lexer = Lexer()
        tokens = lexer.lex_file(template)
        parser = DefaultParser(tokens)
        program = parser.parse()
        code = DefaultRenderer.generate_pre_code(program)
        self._cache[template] = code

        return DefaultRenderer.render_pre(code, **kwargs)

    def _add_header(self, header_name, header_value):
        """
        Example header_name = Content-Type and header_value = text/html
        """
        self.headers[header_name] = header_value

    def _encode(self):
        """
        encode the response with utf-8, so we can send it over http/https
        """
        return self._build_response().encode("utf-8")

    def _build_response(self) -> str:
        """
        builds an HTTP request that we can send to the user.
        """
        if self.error:
            self.contents = [self.error]
            self.headers = {}

        if not self.content_type:
            self.content_type = "text/html"

        response: str = (
            f"HTTP/{self.http_version} 200 OK\nContent-Type: {self.content_type}\n"
        )

        for k, v in self.headers.items():
            response += f"{k}: {v}\n"

        # automatically generate cookies for the user
        response += self._cookie_jar.get_http_cookies()

        response += "\n\n"
        response += "\n".join(self.contents)

        return response
