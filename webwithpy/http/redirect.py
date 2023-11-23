class Redirect:
    def __init__(self, location: str = "/"):
        self.location = location

    def __str__(self):
        return f"""HTTP/1.1 301 Moved Permanently\nLocation: {self.location}"""
