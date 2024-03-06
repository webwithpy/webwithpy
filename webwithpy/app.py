from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .http.request import Request
    from .http.response import Response
    from .http.redirect import Redirect


class App:
    server_path: str = None
    request: Request = None
    response: Response = None
    redirect: Redirect = None
