import sys
import socket
import asyncio
import warnings
import ssl

from asyncio.events import AbstractEventLoop
from .http.handler import HTTPHandler
from .app import App

SERVER_HOST = None
SERVER_PORT = None
SSL_CERTIFICATE_PATH = None
SSL_PRIVATE_KEY_PATH = None


def run_server(
    server_host="127.0.0.1",
    server_port=8000,
    ssl_certificate_path="path/to/your/certificate.pem",
    ssl_private_key_path="path/to/your/private-key.pem",
    use_ssl=False,
):
    global SERVER_HOST, SERVER_PORT, SSL_CERTIFICATE_PATH, SSL_PRIVATE_KEY_PATH

    current_py_version = sys.version_info
    if current_py_version.major != 3 or current_py_version.minor < 12:
        warnings.warn(
            "current python version is deprecated! whenever official py 3.13 launches <=py3.12 will be"
            " unsupported.\nuse of py3.12 is recommended for longest support!",
            DeprecationWarning,
        )

    SERVER_HOST, SERVER_PORT = server_host, server_port
    SSL_CERTIFICATE_PATH, SSL_PRIVATE_KEY_PATH = (
        ssl_certificate_path,
        ssl_private_key_path,
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((server_host, server_port))
    server.setblocking(False)
    server.listen(1)
    loop = asyncio.new_event_loop()

    print(f"server started on {server_host}:{server_port}")

    try:
        if use_ssl:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(SSL_CERTIFICATE_PATH, SSL_PRIVATE_KEY_PATH)
            ssl_context.verify_mode = ssl.VerifyMode.CERT_REQUIRED
            ssl_context.set_ciphers(
                "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
            )
        else:
            ssl_context = None

        loop.run_until_complete(load_clients(server, loop, ssl_context))
    except KeyboardInterrupt:
        # Make sure we don't throw an error when we exit the server
        print("server closed!")


async def load_clients(
    server: socket.socket, loop: AbstractEventLoop, ssl_context: ssl.SSLContext
):
    try:
        while True:
            # connect with client
            client_conn, client_addr = await loop.sock_accept(server)
            reader, writer = await asyncio.open_connection(
                sock=client_conn, ssl=ssl_context
            )
            client_request: str = (await reader.read(2048)).decode()

            # add request to app
            App.server_path = SERVER_HOST

            http_handler = HTTPHandler()
            await loop.create_task(
                http_handler.handle_client(
                    server=loop,
                    client=client_conn,
                    writer=writer,
                    client_request=client_request,
                )
            )

            await writer.drain()
            writer.close()
            await writer.wait_closed()

    except KeyboardInterrupt:
        server.close()
