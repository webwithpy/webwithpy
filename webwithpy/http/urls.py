class Url:
    @classmethod
    def http(cls, path: str, **kwargs):
        """
        will turn any path into a url
        """
        if not path.startswith("/"):
            path = f"/{path}"
        path = f"{path}{'?' if len(kwargs) > 0 else ''}"

        for idx, (key, value) in enumerate(kwargs.items()):
            path += f'{"&" if idx > 0 else ""}{key}={value}'

        return path

    def __call__(self, *args, **kwargs):
        """
        trick whenever someone import url instance(not the class) and does url('path') it will intercept all function
        calls and only call self.http.

        so whenever we do url('path') it will call self.http(path='path')
        """
        return self.http(*args, **kwargs)


url = Url()
