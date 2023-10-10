from ..routing.router import Router
from .request import Request
from .response import Response
from asyncio import AbstractEventLoop, StreamWriter
import socket
import asyncio


class HTTPHandler:
    def __init__(self):
        self.server = None
        self.client = None
        self.writer = None
        self.request = None
        self.resp = None

    async def handle_client(
        self,
        server: AbstractEventLoop,
        client: socket.socket,
        writer: StreamWriter,
        client_request: str,
    ):
        self.server = server
        self.client = client
        self.writer = writer
        self.request: Request = Request(client_request)
        self.resp: Response = Response()

        HTTPHandler.loop = server
        try:
            routed_data = Router.get_data_by_route(self.request.path, self.request.method)

            if routed_data is None:
                await self.send_response(self.resp.generate_error(500))
                return

            func_out = await routed_data.func() if self.async_func(routed_data.func) else routed_data.func()
            self.resp.add_content(
                func_out, routed_data.html_template
            )
        except Exception as e:
            await self.send_response(self.resp.generate_error(500))
            raise e

        # only send response after try catch bc if something goes wrong while sending the response it will give
        # a completely different exception
        await self.send_response(self.resp.encode())

    async def send_response(self, resp: bytes | str = b""):
        if isinstance(resp, str):
            resp = resp.encode()

        self.writer.write(resp)

    async def close_server(self):
        self.client.close()

    @classmethod
    def async_func(cls, func) -> bool:
        return asyncio.iscoroutinefunction(func)