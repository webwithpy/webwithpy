from os import PathLike
from typing import Union


class RouteData:
    def __init__(self, func, url: str, method: str, template: Union[str, PathLike]):
        self.func = func
        self.url = url
        self.method = method
        self.html_template = template

    def eq(self, url, method):
        return self.url == url and (self.method.lower() == method.lower() or self.method.lower() == "any")

    def __str__(self):
        return self.url + " " + self.method

    def __repr__(self):
        return self.__str__()


class Router:
    routes: list[RouteData] = []

    @classmethod
    def get_data_by_route(cls, url: str, method: str):
        for route in Router.routes:
            if route.eq(url, method):
                return route

        return None
