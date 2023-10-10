from typing import Union, Any
from os import PathLike
from ..html import Lexer, DefaultParser, DefaultRenderer


class Response:
    def __init__(self):
        self.http_version: str = "1.1"
        self.content_type: str = "text/html"
        self.headers = {}
        self.contents = []
        self.cache = {}

    def add_content(self, content: Any, template: Union[str, PathLike] = ""):
        # TODO: if template exists add this to html file
        # TODO: parse dict
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

    def encode(self):
        return self.build_response().encode("utf-8")

    def build_response(self) -> str:
        response: str = f"HTTP/{self.http_version}\nContent-Type: {self.content_type}\n"

        for k, v in self.headers:
            response += f"{k}: {v}\n"

        response += "\n"
        response += "\n".join(self.contents)

        return response

    def generate_error(self, code=500):
        if code == 500:
            return f"HTTP/{self.http_version} 500 SERVER ERROR\n\n<h1>Unexpected Exception</h1>"

        return f"HTTP/{self.http_version} 500 SERVER ERROR\n\n<h1>Unexpected Error Code(Not Implemented)</h1>"

    def use_json(self):
        self.content_type = "text/json"
