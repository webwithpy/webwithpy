from ..exeptions.RouteExceptions import RouteNotFound
from ..routing.router import Router
from ..app import App
from .request import Request
from .response import Response
from asyncio import AbstractEventLoop, StreamWriter
from pathlib import Path
import socket
import asyncio
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
        except Exception as e:
            await self.send_response(self.resp._generate_error(500))
            traceback.print_exception(e)
            return

        await self.send_response(self.resp._encode())

    async def call_func_by_route(self, route: str, method):
        routed_data = Router.get_data_by_route(route, method)

        if routed_data is None:
            return await self.handle_static_file(route, method)

        try:
            result = await self.call_routed_func(
                routed_data.func, *routed_data.args, **routed_data.kwargs
            )

            return result, routed_data.html_template, routed_data.content_type
        except Exception as e:
            print(
                f"Error executing function for route {route} and method {method}: {e}"
            )
            traceback.print_exception(e)

            return self.resp._generate_error(500), None, None

    async def call_routed_func(self, func, *args, **kwargs):
        if self.async_func(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    async def handle_static_file(self, route: str, method: str):
        if (file := Router.static_file_by_route(route)) is not None:
            return file, "", f"text/{Router.parse_suffix(Path(route).suffix)}"

        await self.send_response(self.resp._generate_error(404))
        return RouteNotFound(route, method), None, None

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
    def async_func(cls, func) -> bool:
        """
        tests if the function is async or not
        """
        return asyncio.iscoroutinefunction(func)

    @classmethod
    def generate_session(cls):
        """
        Generate a session key for any user connecting to the server
        """
        key = f"{uuid.uuid4()}-{uuid.uuid4()}"
        return key.replace("\r", "")
