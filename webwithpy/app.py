from aiohttp.web_request import Request
import logging


class App(object):

    def __init__(self):
        self.req: Request = None

        # setup logger
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        self.log.addHandler(handler)
