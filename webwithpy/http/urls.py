from ..app import App


class Url:
    def http(self, path: str, **kwargs):
        if not path.startswith('/'):
            path = f'/{path}'
        path = f"{path}{'?' if len(kwargs) > 0 else ''}"

        for idx, key, value in enumerate(kwargs):
            path += f'{"&" if idx > 0 else ""}{key}={value}'

        return path

    def __call__(self, *args, **kwargs):
        return self.http(*args, **kwargs)


url = Url()
