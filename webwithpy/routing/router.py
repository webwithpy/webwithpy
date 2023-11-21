from os import PathLike
from typing import Union


class RouteData:
    def __init__(self, func, url: str, method: str, template: Union[str, PathLike, None], *args, **kwargs):
        self.func = func
        self.url = url
        self.method = method
        self.html_template = template
        self.args = args
        self.kwargs = kwargs

    def get_route(self):
        return self.url

    def eq(self, url, method):
        return self.url == url and (self.method.lower() == method.lower() or self.method.lower() == "any")

    def __str__(self):
        return f"{self.method.upper()} + {self.url.lower()}"

    def __repr__(self):
        return self.__str__()


class Router:
    routes: list[RouteData] = []

    @classmethod
    def add_route(cls, func, url: str, method: str, template: str = ''):
        Router.routes.append(RouteData(func, url, method, template))

    @classmethod
    def get_data_by_route(cls, url: str, method: str):
        for route in Router.routes:
            if route.eq(url, method):
                return route

        return None

    @classmethod
    def get_route(cls, route: str):
        for Router_route in Router.routes:
            if Router_route.get_route() == route:
                return Router_route
        return None
