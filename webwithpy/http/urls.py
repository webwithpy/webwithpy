class Url:
    @classmethod
    def http(cls, path: str, **kwargs):
        if not path.startswith('/'):
            path = f'/{path}'
        path = f"{path}{'?' if len(kwargs) > 0 else ''}"
    
        for idx, (key, value) in enumerate(kwargs.items()):
            path += f'{"&" if idx > 0 else ""}{key}={value}'

        return path

    def __call__(self, *args, **kwargs):
        return self.http(*args, **kwargs)


url = Url()
