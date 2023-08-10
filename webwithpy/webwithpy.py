from webwithpy.request_handlers import HttpHandler
from .wwp_streams.html import HtmlData
from aiohttp import web
from aiohttp.web_app import Application
import asyncio


def add_routes_to_server(app: Application):
    for route in HtmlData.req_paths:
        app.router.add_route(route["request_type"], route["url"], HttpHandler.do_GET if route["request_type"] else HttpHandler.do_POST)


def run_server():
    # TODO: make socket selectable via settings
    loop = asyncio.new_event_loop()
    loop.create_task(run_web_app())
    loop.run_forever()

    print(f'Server started running at ??')


async def run_web_app() -> int:
    it = 0
    app = web.Application()

    add_routes_to_server(app)

    runner = web.AppRunner(app)
    await runner.setup()

    while True:
        try:
            server = web.TCPSite(runner, '127.0.0.1', 8000 + it)
            await server.start()
        except OSError:
            it += 1
            continue
        finally:
            break

    return it
