from .http.request import Request


class App:
    server_path = None
    request: Request = None
    sessions = {}
