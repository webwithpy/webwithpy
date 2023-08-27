from .router import Router, RouteData


def GET(url="/", template=""):
    def inner(func):
        Router.routes.append(RouteData(func=func, url=url, method="GET", template=template))

    return inner


def POST(url="/", template=""):
    def inner(func):
        Router.routes.append(RouteData(func=func, url=url, method="POST", template=template))

    return inner


def ANY(url="/", template=""):
    def inner(func):
        Router.routes.append(RouteData(func=func, url=url, method="ANY", template=template))

    return inner
