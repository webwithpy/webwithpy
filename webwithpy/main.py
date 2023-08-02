from http.server import HTTPServer
from wwp_handler.request_handlers import HttpHandler


def run_http_server():
    server_addr = ('127.0.0.1', 8000)
    server = HTTPServer(server_addr, HttpHandler)
    print(f'Server started running at {server_addr}')
    server.serve_forever()


if __name__ == "__main__":
    run_http_server()
