from ..routing.router import Router
from .request import Request
from .response import Response
from ..app import App
from asyncio import AbstractEventLoop, StreamWriter
import socket
import asyncio
import traceback
import uuid


class HTTPHandler:
    def __init__(self):
        self.server = None
        self.client = None
        self.writer = None
        App.request = None
        self.resp = None

    async def handle_client(
        self,
        server: AbstractEventLoop,
        client: socket.socket,
        writer: StreamWriter,
        client_request: str,
    ):
        """
        Handles the client request by setting cookies, finding the function by the clients path and sending a request
        back
        """
        self.server = server
        self.client = client
        self.writer = writer
        App.request = Request(client_request)

        # make a response object with a new session or the current session given by the request
        self.resp: Response = Response(App.request.cookies.get('session', f"{uuid.uuid4()}{uuid.uuid4()}"))
        
        # Make sure if the session does not exist the session is set in App.request.cookies
        if "session" not in App.request.cookies:
            App.request.cookies["session"] = self.resp.cookies["session"]

        #  try to find the function by the request path
        try:
            routed_data = Router.get_data_by_route(App.request.path, App.request.method)

            if routed_data is None:
                print(f"User tried to go to this path: {App.request.path} with this method: {App.request.method},"
                      f" However it was not found or it could not be accessed with this request method!")

                # send a 404 not found back because the path->method->function was not found!
                await self.send_response(self.resp.generate_error(404))
                return

            # run the function and send the data back to the user
            func_out = await routed_data.func() if self.async_func(routed_data.func) else routed_data.func()
            self.resp.add_content(
                func_out, routed_data.html_template
            )
        except Exception as e:
            # it is possible that a response
            await self.send_response(self.resp.generate_error(500))
            traceback.print_exception(e)
            return

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
        """
        tests if the function is async or not
        """
        return asyncio.iscoroutinefunction(func)
