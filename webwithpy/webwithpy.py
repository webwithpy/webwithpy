import socket
import asyncio

from asyncio.events import AbstractEventLoop
from .http.handler import HTTPHandler
from .app import App

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000


def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.setblocking(False)
    server.listen(1)
    loop = asyncio.new_event_loop()

    print(f"server started on {SERVER_HOST}:{SERVER_PORT}")

    try:
        loop.run_until_complete(load_clients(server, loop))
    except KeyboardInterrupt:
        # Make sure we don't throw an error when we exit the server
        print("server closed!")


async def load_clients(server: socket.socket, loop: AbstractEventLoop):
    try:
        while True:
            # connect with client
            client_conn, client_addr = await loop.sock_accept(server)
            reader, writer = await asyncio.open_connection(sock=client_conn)
            client_request: str = (await reader.read(2048)).decode()

            # add request to app
            App.server_path = SERVER_HOST

            http_handler = HTTPHandler()
            await loop.create_task(
                http_handler.handle_client(
                    server=loop,
                    client=client_conn,
                    writer=writer,
                    client_request=client_request
                )
            )

            await writer.drain()
            writer.close()
            await writer.wait_closed()

    except KeyboardInterrupt:
        server.close()
