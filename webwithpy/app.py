from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .http.request import Request


class App:
    server_path = None
    request: Request = None
    response = None
    redirect = None
