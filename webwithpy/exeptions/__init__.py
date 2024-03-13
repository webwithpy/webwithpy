class HttpException(Exception):
    def __init__(self, error_type: str, message: str):
        self.message = message
        self.error_type = error_type
        super(HttpException, self).__init__(self.__str__())

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"HTTP/1.1 {self.error_type}\n\n<h1>{self.message}</h1>"


class FileNotFound(HttpException):
    def __init__(self, message: str):
        super().__init__("404 Not Found", message)


class Forbidden(HttpException):
    def __init__(self, message: str):
        super().__init__("401 Unauthorized", message)


class ServerError(HttpException):
    def __init__(self, message: str):
        super().__init__("500 Internal Server Error", message)


class MethodNotImplemented(HttpException):
    def __init__(self, message: str):
        super().__init__("501 Not Implemented", message)
