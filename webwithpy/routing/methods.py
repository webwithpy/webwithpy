from ..exeptions.RouteExceptions import RouteFound
from .router import Router, RouteData
from typing import Callable


def check_path_exists(func: Callable, route: str):
    route_data = Router._get_route(route)

    if route_data is not None:
        raise RouteFound(route, method=func, defined_method=route_data.func)


def GET(url="/", template="", content_type=""):
    url = fix_url(url)

    def inner(func, *args, **kwargs):
        check_path_exists(func, url)
        Router.routes.append(
            RouteData(
                func=func,
                url=url,
                method="GET",
                template=template,
                content_type=content_type,
                *args,
                **kwargs,
            )
        )

    return inner


def POST(url="/", template="", content_type=""):
    url = fix_url(url)

    def inner(func, *args, **kwargs):
        check_path_exists(func, url)
        Router.routes.append(
            RouteData(
                func=func,
                url=url,
                method="POST",
                template=template,
                content_type=content_type,
                *args,
                **kwargs,
            )
        )

    return inner


def ANY(url="/", template="", content_type=""):
    url = fix_url(url)

    def inner(func, *args, **kwargs):
        check_path_exists(func, url)
        Router.routes.append(
            RouteData(
                func=func,
                url=url,
                method="ANY",
                template=template,
                content_type=content_type,
                *args,
                **kwargs,
            )
        )

    return inner


def fix_url(url: str):
    if len(url) == 0 or url[0] != "/":
        url = f"/{url}"
    return url
