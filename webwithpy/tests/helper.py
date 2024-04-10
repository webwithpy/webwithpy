from ..routing.router import Router, RouteData
from ..routing.methods import fix_url, check_path_exists


def test_function(url="/"):
    url = fix_url(url)

    def inner(func, *args, **kwargs):
        check_path_exists(func, url)
        Router.routes.append(
            RouteData(
                func=func,
                url=url,
                method="ANY",
                template="",
                content_type="",
                test_function=True,
                *args,
                **kwargs,
            )
        )

    return inner
