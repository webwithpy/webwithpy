from ..exeptions.RouteExceptions import RouteNotFound
from ..routing.router import Router
from .response import Response
from .request import MultipartHTTPRequestParser, FormURLEncodedHTTPRequestParser
from ..app import App
from asyncio import AbstractEventLoop, StreamWriter
import socket
import traceback
import uuid


class HTTPHandler:
    def __init__(
        self,
        server: AbstractEventLoop,
        client: socket.socket,
        writer: StreamWriter,
        client_request: bytes,
    ):
        self.server = server
        self.client = client
        self.writer = writer
        App.request = self.choose_parser(client_request)

        session = self.manage_session()
        self.resp: Response = Response(session)
        App.response = self.resp

    async def handle_client(self):
        try:
            func_out, html_template, content_type = await Router._call_func_by_route(
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
            await self.send_response(e.__str__())
            traceback.print_exception(e)
            return

        await self.send_response(self.resp._encode())

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
    def choose_parser(cls, raw_request: bytes):
        headers = raw_request.split(b"\r\n")
        for line in headers:
            if line.startswith(b"Content-Type:"):
                content_type = line.split(b": ")[1]
                if b"multipart/form-data" in content_type:
                    return MultipartHTTPRequestParser(raw_request)
                elif b"application/x-www-form-urlencoded" in content_type:
                    return FormURLEncodedHTTPRequestParser(raw_request)
        # Default to MultipartHTTPRequestParser if content type not found
        return MultipartHTTPRequestParser(raw_request)

    @classmethod
    def generate_session(cls):
        """
        Generate a session key for any user connecting to the server
        """
        key = f"{uuid.uuid4()}-{uuid.uuid4()}"
        return key.replace("\r", "")
