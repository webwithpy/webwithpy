from .router import Router, RouteData


def GET(url="/", template=""):
    url = fix_url(url)
    def inner(func):
        Router.routes.append(RouteData(func=func, url=url, method="GET", template=template))

    return inner


def POST(url="/", template=""):
    url = fix_url(url)
    def inner(func):
        Router.routes.append(RouteData(func=func, url=url, method="POST", template=template))

    return inner


def ANY(url="/", template=""):
    url = fix_url(url)
    def inner(func):
        Router.routes.append(RouteData(func=func, url=url, method="ANY", template=template))

    return inner

def fix_url(url: str):
    if len(url) == 0 or url[0] != '/':
        url = f'/{url}'
    return url