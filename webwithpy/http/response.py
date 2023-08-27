from typing import Union
from os import PathLike
from ..html.pyht import HtmlFile


class Response:
    def __init__(self):
        self.http_version: str = "1.1"
        self.content_type: str = "text/html"
        self.headers = {}
        self.contents = []

    def add_content(self, content: str, template: Union[str, PathLike] = ""):
        # TODO: if template exists add this to html file
        # TODO: parse dict
        self.contents.append(str(content))
        if template != '':
            html_file = HtmlFile(path=template)
            self.contents.append(html_file.render())

    def add_header(self, header_name, header_value):
        """
        Example header_name = Content-Type and header_value = text/html
        """
        self.headers[header_name] = header_value

    def encode(self):
        return self.build_response().encode('utf-8')

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
