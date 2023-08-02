from http.server import BaseHTTPRequestHandler
from wwp_data.html_data import HtmlData


class HttpHandler(BaseHTTPRequestHandler):
    @classmethod
    def parse_http_handler_req(cls, handler, method):
        handler.send_response(200)
        handler.send_header('Content-type', 'text/html')
        handler.end_headers()

        # load function that has the req path and is a GET request
        req_func = HtmlData.search_req_paths(handler.path, method)

        if not req_func:
            handler.wfile.write(b"path not found!")
            return


        handler.wfile.write(str(req_func["func"]()).encode('utf-8'))

    def do_GET(self):
        self.parse_http_handler_req(self, "GET")

    def do_POST(self):
        self.parse_http_handler_req(self, "POST")
