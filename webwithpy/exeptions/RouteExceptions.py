import inspect
from typing import Callable


class RouteFound(Exception):
    def __init__(self, route: str, method: Callable = None, defined_method: Callable = None):
        self.message = f"Route is already in use: {route}"

        if method is not None:
            self.message += f" in {inspect.getfile(method)}"
        if defined_method is not None:
            self.message += f" and {inspect.getfile(defined_method)}"

        super(self, RouteFound).__init__(self.message)
