import base64
import socket
import asyncio
import ssl

from asyncio.events import AbstractEventLoop
from .http.handler import HTTPHandler
from .app import App


def run_server(
    server_host="127.0.0.1",
    server_port=8000,
    ssl_certificate_path="path/to/your/certificate.pem",
    ssl_private_key_path="path/to/your/private-key.pem",
    use_ssl=False,
):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((server_host, server_port))
    server.setblocking(False)
    server.listen(1)
    loop = asyncio.new_event_loop()

    print(f"server started on {server_host}:{server_port}")

    ssl_context = (
        generate_ssl_context(ssl_certificate_path, ssl_private_key_path)
        if use_ssl
        else None
    )

    try:
        loop.run_until_complete(load_clients(server, loop, ssl_context, server_host))
    except KeyboardInterrupt:
        # Make sure we don't throw an error when we exit the server
        print("server closed!")


def generate_ssl_context(
    ssl_certificate_path="path/to/your/certificate.pem",
    ssl_private_key_path="path/to/your/private-key.pem",
):
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(ssl_certificate_path, ssl_private_key_path)
    ssl_context.verify_mode = ssl.VerifyMode.CERT_REQUIRED
    ssl_context.set_ciphers("ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384")

    return ssl_context


async def load_clients(
    server: socket.socket,
    loop: AbstractEventLoop,
    ssl_context: ssl.SSLContext,
    host: str,
):
    try:
        while True:
            # connect with client
            client_conn, client_addr = await loop.sock_accept(server)
            reader, writer = await asyncio.open_connection(
                sock=client_conn, ssl=ssl_context
            )
            request = bytes()
            while True:
                chunk = await reader.read(1024)
                request += chunk
                if len(chunk) < 1024:
                    break
            # add request to app
            App.server_path = host

            await loop.create_task(
                HTTPHandler(
                    server=loop,
                    client=client_conn,
                    writer=writer,
                    client_request=request,
                ).handle_client()
            )

            await writer.drain()
            writer.close()
            await writer.wait_closed()

    except KeyboardInterrupt:
        server.close()
