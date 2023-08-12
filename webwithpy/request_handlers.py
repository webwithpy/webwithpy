from .streams.html import HtmlData
from .streams import HtmlFile, Download
from .app import App
from aiohttp import web
from http.server import BaseHTTPRequestHandler
import inspect


class HttpHandler(BaseHTTPRequestHandler):
    @classmethod
    async def parse_http_handler_req(cls, handler, method):
        """
        generates a web response from the given request 'get' or 'post'
        """
        App.req = handler
        cls.handler = handler
        cls.req_type = method

        # load function that has the req path and is a GET request
        req_func = HtmlData.search_req_paths(handler.path, method)

        if not req_func:
            return b"path not found!"

        return await cls._handle_req_func(req_func["func"])

    @classmethod
    async def _handle_req_func(cls, func):
        """
        gets the output of any function given by the user of the framework
        async or not.
        """
        func_out = func() if not await cls.isAsync(func) else await func()

        return await cls.render_web_response(func_out)

    @classmethod
    async def isAsync(cls, someFunc):
        """
        Returns a true or false if the give 'someFunc' is async
        This mainly is used for loading in functions made by people that
        use this framework
        """
        return inspect.iscoroutinefunction(someFunc)

    @classmethod
    async def render_web_response(cls, func_out):
        """
        this function attempts to correctly parse any functions output

        :param func_out: Any
        """
        if isinstance(func_out, HtmlFile):
            rendered_html_text = await func_out.jinja_html_render(cls.handler)
            return web.Response(text=rendered_html_text, content_type="text/html")
        elif isinstance(func_out, Download):
            resp = web.Response(text="hi")
            # resp = await cls.render_web_response(func_out.text)
            resp = await func_out.stream_download(resp, cls.handler)

            return resp
        elif isinstance(func_out, dict):
            return web.json_response(func_out)

        return web.Response(text=str(func_out), content_type="text/html")

    async def do_GET(self):
        return await HttpHandler.parse_http_handler_req(self, "GET")

    async def do_POST(self):
        return await HttpHandler.parse_http_handler_req(self, "POST")

