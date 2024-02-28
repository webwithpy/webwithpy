from ..exeptions.RouteExceptions import RouteNotFound
from ..routing.router import Router
from ..app import App
from .redirect import Redirect
from .request import Request
from .response import Response
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

        session = (
            self.generate_session()
            if "session" not in App.request.cookies
            else App.request.cookies["session"]
        )

        # make a response object with a new session or the current session given by the request
        self.resp: Response = Response(session)
        App.response = self.resp

        #  try to find the function by the request path
        try:
            func_out, html_template, content_type = await self.call_func_by_route(
                App.request.path, App.request.method
            )

            self.resp.content_type = content_type

            # make sure we never send any data with the response is 404(DON'T REMOVE CAN LEAK DATA IF REMOVED)
            if isinstance(func_out, RouteNotFound):
                return
            elif App.redirect is not None:
                # function is only protected for people who use the framework, the framework itself can always call
                # protected functions
                await self.send_response(App.redirect._to_http())
                return
            self.resp.add_content(func_out, html_template)
        except Exception as e:
            # it is possible that a response
            await self.send_response(self.resp.generate_error(500))
            traceback.print_exception(e)
            return

        # only send response after try catch bc if something goes wrong while sending the response it will give
        # a completely different exception
        await self.send_response(self.resp.encode())

    async def call_func_by_route(self, route, method):
        """
        Runs a function based on the request method and route
        :return: function output and html template
        """
        routed_data = Router.get_data_by_route(route, method)

        if routed_data is None:
            print(
                f"User tried to go to this path: {App.request.path} with this method: {App.request.method},"
                f" However it was not found or it could not be accessed with this request method!"
            )

            # send a 404 not found back because the path->method->function was not found!
            await self.send_response(self.resp.generate_error(404))
            return RouteNotFound(route, method), None, None

        # we will need to awaut the routed function if it is async!
        if self.async_func(routed_data.func):
            return (
                await routed_data.func(*routed_data.args, **routed_data.kwargs),
                routed_data.html_template,
                routed_data.content_type,
            )

        # run routed function no async
        return (
            routed_data.func(*routed_data.args, **routed_data.kwargs),
            routed_data.html_template,
            routed_data.content_type,
        )

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
