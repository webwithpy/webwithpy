from http.server import HTTPServer
from .wwp_handler.request_handlers import HttpHandler


def run():
    # TODO: make socket selectable via settings
    it = 0
    while True:
        server_addr = ('127.0.0.1', 8000)
        try:
            server = HTTPServer(server_addr, HttpHandler)
        except OSError:
            it += 1
            continue
        finally:
            break

    print(f'Server started running at {server_addr}')

    # try to close server of the socket so it can run on the same socket again
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()