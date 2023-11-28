from .http.request import Request


class App:
    server_path = None
    request: Request = None
    response = None
    redirect = None
