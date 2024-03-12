import os
from os import PathLike
from typing import Union
from pathlib import Path

from webwithpy.exeptions.RouteExceptions import RouteNotFound

from webwithpy.exeptions import ServerError
from webwithpy.helper.async_handler import HandleAsync


class RouteData:
    def __init__(
        self,
        func,
        url: str,
        method: str,
        template: Union[str, PathLike, None],
        content_type: str,
        *args,
        **kwargs,
    ):
        self.func = func
        self.url = url
        self.method = method
        self.html_template = template
        self.args = args
        self.kwargs = kwargs
        self.content_type = content_type

    async def call_func(self, _async: bool):
        """
        calls function and returns necessary data to turn it into a http request
        """
        if _async:
            return (
                await self.func(*self.args, **self.kwargs),
                self.html_template,
                self.content_type,
            )

        return (
            self.func(*self.args, **self.kwargs),
            self.html_template,
            self.content_type,
        )

    def get_route(self):
        # getter for url
        return self.url

    def eq(self, url: str, method: str) -> bool:
        # checks if url and method is equal to current routed data
        return self.url == url and (
            self.method.lower() == method.lower() or self.method.lower() == "any"
        )

    def __str__(self):
        # if routed_data is printed it will print the method and url instead of its memory location
        return f"{self.method.upper()} + {self.url.lower()}"

    def __repr__(self):
        return self.__str__()


class Router:
    # python hack for static vars
    routes: list[RouteData] = []

    @classmethod
    def add_route(
        cls, func, url: str, method: str, template: str = "", content_type: str = ""
    ):
        """
        adds routes to the router
        """
        Router.routes.append(RouteData(func, url, method, template, content_type))

    @classmethod
    def get_data_by_route(cls, url: str, method: str) -> RouteData | None:
        """
        gets the routed data by route

        :param url: http url like '/route'
        :param method: method used by http
        """
        for route in Router.routes:
            if route.eq(url, method):
                return route

        return None

    @classmethod
    def get_route(cls, route: str):
        """
        gets the routed data by route

        :param route: route is simple an url in this case: '/route'
        """
        for Router_route in Router.routes:
            if Router_route.get_route() == route:
                return Router_route
        return None

    @classmethod
    def static_file_by_route(cls, route: str):
        path = Path(f"{os.getcwd()}/static{route}")

        if path.exists():
            return path.read_text()

        return None

    @classmethod
    def parse_suffix(cls, suffix: str):
        known_suffix = {".css": "css", ".js": "javascript"}

        return known_suffix[suffix]

    @classmethod
    async def call_func_by_route(cls, route: str, method: str):
        routed_data = cls.get_data_by_route(route, method)

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
