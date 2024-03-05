from asyncio import AbstractEventLoop, StreamWriter
from socket import socket

from .packet import PacketHandler
from .request import Request
from ..app import App


class ClientHandler:
    def __init__(
        self,
        server: AbstractEventLoop,
        client: socket,
        writer: StreamWriter,
        client_request: str,
    ):
        self.server = server
        self.client = client
        self.writer = writer
        self.packet = PacketHandler(client_request).generate_packet()
        App.request = Request(client_request)

    def handle_request(self):



