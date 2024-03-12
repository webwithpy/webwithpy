class HttpException(Exception):
    def __init__(self, error_type: str, message: str):
        self.message = message
        self.error_type = error_type
        super().__init__(self.__str__())

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"HTTP/1.1 {self.error_type}\n\n<h1>{self.message}</h1>"


class UrlNotFound(HttpException):
    def __init__(self, message: str):
        super().__init__("404 Not Found", message)


class BadRequest(HttpException):
    def __init__(self, message: str):
        super().__init__("400 Bad Request", message)


class ServerError(HttpException):
    def __init__(self, message: str):
        super().__init__("500 Server Error", message)
