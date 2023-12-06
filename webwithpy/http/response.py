from typing import Union, Any
from os import PathLike
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
        self.cache = {}
        self.cookies = {"session": session}

    def add_content(self, content: Any, template: Union[str, PathLike] = ""):
        """
        function will add any content given the user based on if he gave-up a template
        """
        if template != "":
            if not isinstance(content, dict):
                content = {}

            rendered = (
                self.parse_template(template, **content)
                if template not in self.cache
                else DefaultRenderer.render_pre(self.cache[template], **content)
            )
            self.contents.append(rendered)
        else:
            self.contents.append(str(content))

    def parse_template(self, template: Union[str, PathLike], **kwargs):
        """
        will parse the template with htpyp
        """
        lexer = Lexer()
        tokens = lexer.lex_file(template)
        parser = DefaultParser(tokens)
        program = parser.parse()
        code = DefaultRenderer.generate_pre_code(program)
        self.cache[template] = code

        return DefaultRenderer.render_pre(code, **kwargs)

    def add_header(self, header_name, header_value):
        """
        Example header_name = Content-Type and header_value = text/html
        """
        self.headers[header_name] = header_value

    def add_cookie(self, cookie_name, cookie_value):
        """sets a cookie that will be added when building and encoding the resp"""
        self.cookies[cookie_name] = cookie_value

    def encode(self):
        """
        encode the response with utf-8, so we can send it over http/https
        """
        return self.build_response().encode("utf-8")

    def build_response(self) -> str:
        """
        builds an HTTP request that we can send to the user.
        """
        response: str = (
            f"HTTP/{self.http_version} 200 OK\nContent-Type: {self.content_type}\n"
        )

        for k, v in self.headers.items():
            response += f"{k}: {v}\n"

        for k, v in self.cookies.items():
            self.cookies[k] = str(v).replace("\r", "")

        for name, value in self.cookies.items():
            # Max-Age of all cookies is currently required, this will be change after 1.0
            response += f"Set-Cookie: {name}={value}; Max-Age=86400\n"

        response += "\n\n"
        response += "\n".join(self.contents)

        return response

    def generate_error(self, code=500):
        """
        the only errors we currently support is or 500 or 404
        """
        self.headers = {}
        self.contents = []

        if code == 500:
            return (
                f"HTTP/{self.http_version} 500 SERVER ERROR\n\n<h1>SERVER ERROR!</h1>"
            )

        return f"HTTP/{self.http_version} 404 NOT FOUND\n\n<h1>PAGE NOT FOUND!</h1>"
