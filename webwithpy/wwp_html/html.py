from pathlib import Path
from starlette.templating import Jinja2Templates

class HtmlFile:
    def __init__(self, path, **kwargs):
        temp_path = Path(path)
        self.path = str(temp_path.parents[0])
        self.file_name = temp_path.name
        self.templates = Jinja2Templates(directory=self.path)
        self.jinja_args = kwargs

    def load(self, handler):
        args = self.jinja_args
        args.update({"request": handler})
        template = self.templates.get_template(self.file_name)
        response = template.render(args)
        return response.encode()
