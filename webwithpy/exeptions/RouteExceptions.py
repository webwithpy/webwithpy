import inspect
from typing import Callable


class RouteException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class RouteFound(RouteException):
    def __init__(
        self, route: str, method: Callable = None, defined_method: Callable = None
    ):
        self.message = f"Route {route} is already in use"

        if method is not None:
            self.message += f" in files {inspect.getfile(method)}"
        if defined_method is not None:
            self.message += f" and {inspect.getfile(defined_method)}"

        super().__init__(self.message)


class RouteNotFound(RouteException):
    def __init__(self, route: str, request_method: str):
        self.message = f"Route {route}:{request_method} is not found!"

        super().__init__(self.message)
