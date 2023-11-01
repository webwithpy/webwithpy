from typing import Union, Any
from os import PathLike
from ..html.lexer import Lexer
from ..html.parser import DefaultParser
from ..html.renderer import DefaultRenderer


class Response:
    def __init__(self, session):
        self.http_version: str = "1.1"
        self.content_type: str = "text/html"
        self.headers = {}
        self.contents = []
        self.cache = {}
        self.cookies = {"session": session, "test": 1}

    def add_content(self, content: Any, template: Union[str, PathLike] = ""):
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
        self.cookies[cookie_name] = cookie_value

    def encode(self):
        return self.build_response().encode("utf-8")

    def build_response(self) -> str:
        response: str = f"HTTP/{self.http_version} 200 OK\nContent-Type: {self.content_type}\n"

        for k, v in self.headers.items():
            response += f"{k}: {v}\n"

        for k, v in self.cookies.items():
            self.cookies[k] = str(v).replace('\r', '')

        response += f"Set-Cookie: {';'.join([f'{k}={v}' for k, v in self.cookies.items()])}"
        response += "\n\n"
        response += "\n".join(self.contents)

        return response

    def generate_error(self, code=500):
        self.headers = {}
        self.contents = []

        if code == 500:
            return f"HTTP/{self.http_version} 500 SERVER ERROR\n\n<h1>SERVER ERROR!</h1>"

        return f"HTTP/{self.http_version} 404 NOT FOUND\n\n<h1>PAGE NOT FOUND!</h1>"

    def use_json(self):
        self.content_type = "text/json"
