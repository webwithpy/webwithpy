from ..exeptions.HttpExceptions import HttpException, BadRequest, ServerError
from ..exeptions.RouteExceptions import RouteException, RouteNotFound
from ..helper.async_handler import HandleAsync
from ..routing.router import Router
from .response import Response
from .request import Request
from ..app import App
from asyncio import AbstractEventLoop, StreamWriter
from pathlib import Path
import socket
import traceback
import uuid


class HTTPHandler:
    def __init__(
        self,
        server: AbstractEventLoop,
        client: socket.socket,
        writer: StreamWriter,
        client_request: str,
    ):
        self.server = server
        self.client = client
        self.writer = writer
        App.request = Request(client_request)

        session = self.manage_session()
        self.resp: Response = Response(session)
        App.response = self.resp

    async def handle_client(self):
        try:
            func_out, html_template, content_type = await self.call_func_by_route(
                App.request.path, App.request.method
            )
            if isinstance(func_out, RouteNotFound):
                return
            self.resp.content_type = content_type
            if App.redirect is not None:
                await self.send_response(App.redirect._to_http())
                return
            self.resp._add_content(func_out, html_template)
        except HttpException | RouteException as e:
            await self.send_response(e.__str__())
            traceback.print_exception(e)
            return

        await self.send_response(self.resp._encode())

    @classmethod
    async def call_func_by_route(cls, route: str, method: str):
        routed_data = Router.get_data_by_route(route, method)

        if routed_data is None:
            return await cls.handle_static_file(route, method)

        try:
            result = await HandleAsync.call_function(
                routed_data.func, *routed_data.args, **routed_data.kwargs
            )

            return result, routed_data.html_template, routed_data.content_type
        except Exception as e:
            print(
                f"Error executing function for route {route} and method {method}: {e}"
            )

            raise ServerError("Server Error!")

    @classmethod
    async def handle_static_file(cls, route: str, method: str):
        if (file := Router.static_file_by_route(route)) is not None:
            return file, "", f"text/{Router.parse_suffix(Path(route).suffix)}"

        raise RouteNotFound(route, method)

    async def send_response(self, resp: bytes | str = b""):
        """
        Writes the response back to the user
        """
        if isinstance(resp, str):
            resp = resp.encode()

        self.writer.write(resp)

    async def close_server(self):
        """
        Closes the connection
        """
        self.client.close()

    def manage_session(self):
        if "session" not in App.request.cookies:
            return self.generate_session()
        return App.request.cookies["session"]

    @classmethod
    def generate_session(cls):
        """
        Generate a session key for any user connecting to the server
        """
        key = f"{uuid.uuid4()}-{uuid.uuid4()}"
        return key.replace("\r", "")
