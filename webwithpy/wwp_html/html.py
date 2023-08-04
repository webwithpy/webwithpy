from pathlib import Path
from starlette.templating import Jinja2Templates


class HtmlFile:
    def __init__(self, path, *args, **kwargs):
        temp_path = Path(path)
        self.path = str(temp_path.parents[0])
        self.file_name = temp_path.name
        self.templates = Jinja2Templates(directory=self.path)
        self.jinja_args = kwargs
        self.jinja_args.update({key: value for key, value in args})

    def __load(self):
        return self.templates.TemplateResponse(self.file_name, self.jinja_args)
