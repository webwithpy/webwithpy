from http.server import BaseHTTPRequestHandler, HTTPServer
from requests.requests import GET
from data.html_data import HtmlData


class HttpHandler(BaseHTTPRequestHandler):
    @classmethod
    def parse_http_handler_req(cls, handler):
        # handler.send_response(200)
        # load function that has the req path and is a GET request
        req_func = HtmlData.search_req_paths(handler.path, "GET")

        if not req_func:
            handler.send_response_only(400)
            return

        handler.send_response(200)
        handler.send_header('Content-type', 'text/html')
        handler.end_headers()
        handler.wfile.write(str(req_func["func"]()).encode('utf-8'))

    def do_GET(self):
        self.parse_http_handler_req(self)


def run_http_server():
    server_addr = ('127.0.0.1', 8000)
    server = HTTPServer(server_addr, HttpHandler)
    print(f'Server started running at {server_addr}')
    server.serve_forever()


if __name__ == "__main__":
    print(HtmlData.req_paths)
    run_http_server()
