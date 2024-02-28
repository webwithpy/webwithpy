from os import PathLike
from typing import Union


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
