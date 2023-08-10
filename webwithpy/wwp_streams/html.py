from pathlib import Path
from starlette.templating import Jinja2Templates


class HtmlFile:
    def __init__(self, path, **kwargs):
        temp_path = Path(path)
        self.path = str(temp_path.parents[0])
        self.file_name = temp_path.name
        self.templates = Jinja2Templates(directory=self.path)
        self.jinja_args = kwargs

    async def jinja_html_render(self, handler) -> str:
        args = self.jinja_args
        args.update({"request": handler})
        template = self.templates.get_template(self.file_name)
        response = template.render(args)
        return response


class HtmlData:
    # list of requests with their function
    # for example if some loads their function with @GET(path='/') then we will store it here.
    req_paths: [] = []

    @classmethod
    def search_req_paths(cls, url, method):
        for rp in cls.req_paths:
            if rp["url"] == url and rp["request_type"] == method:
                return rp

        return False