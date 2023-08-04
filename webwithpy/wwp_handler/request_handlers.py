from http.server import BaseHTTPRequestHandler
from ..wwp_data.html_data import HtmlData
from ..wwp_html import HtmlFile

class HttpHandler(BaseHTTPRequestHandler):
    @classmethod
    def add_default_header_to_handler(cls, handler):
        handler.send_response(200)
        handler.send_header('Content-type', 'text/html')
        handler.end_headers()

    @classmethod
    def parse_http_handler_req(cls, handler, method):
        cls.add_default_header_to_handler(handler)

        # load function that has the req path and is a GET request
        req_func = HtmlData.search_req_paths(handler.path, method)

        if not req_func:
            handler.wfile.write(b"path not found!")
            return

        func_out = cls._handle_req_func(req_func["func"]())

        handler.wfile.write(func_out)

    @classmethod
    def _handle_req_func(cls, out):
        if isinstance(out, HtmlFile):
            return out.__load()
        return str(out).encode('utf-8')

    def do_GET(self):
        self.parse_http_handler_req(self, "GET")

    def do_POST(self):
        self.parse_http_handler_req(self, "POST")
