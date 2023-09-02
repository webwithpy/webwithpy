from pathlib import Path
from typing import List, Any


class HtmlFile:
    def __init__(self, path: str | Path, encoding: str = 'utf-8'):
        self.path = path
        self.encoding = encoding

        if isinstance(self.path, str):
            self.path = Path(self.path).expanduser()
            if not self.path.exists():
                raise FileNotFoundError(f"Couldn't find html file at {self.path}")

        self.html_py_content: list[str] = self.path.read_text(encoding=self.encoding).split('\n')

    def render(self, exec_vars: Any) -> str:
        exec_out = ''
        parser = HtmlParser(html_file_name=self.path.name, exec_out_name="exec_out")
        parsed_html_code = parser.render(self.html_py_content)
        lvars = {'exec_out': exec_out}

        if isinstance(exec_vars, dict):
            lvars.update(exec_vars)
        else:
            lvars["vars"] = exec_vars

        exec(parsed_html_code, globals(), lvars)

        return lvars["exec_out"]


class HtmlParser:
    def __init__(self, html_file_name: str, exec_out_name: str):
        self.parsed_python = ''
        self.html_file_name = html_file_name
        # the name of the variable in locals
        # see HtmlFile.render
        self.exec_out_name = exec_out_name

    def render(self, html_py_content: List[str]) -> str:
        spacing = ''

        for unfiltered_line in html_py_content:
            unfiltered_line = unfiltered_line.strip(' ')
            filtered_line = unfiltered_line[unfiltered_line.find("{{")+2:unfiltered_line.find("}}")]

            if len(filtered_line) == 0 or "{{" not in unfiltered_line:
                continue

            if '=' in filtered_line:
                self.__draw_var(spacing, filtered_line)
            elif 'pass' in filtered_line:
                spacing = spacing[:-4]
            else:
                self.__render_python(spacing, filtered_line)
                if filtered_line[-1] == ':':
                    spacing += "    "

        if spacing != '':
            raise IndentationError(f"The html file {self.html_file_name} cannot be rendered due to a indentation error."
                                   "\n(you probably forgot to add a `{{pass}}` to the code)")

        return self.parsed_python

    def __render_python(self, spacing: str, line: str) -> None:
        self.parsed_python += spacing + line + "\n"

    def __draw_var(self, spacing: str, line: str) -> None:
        current_line = line[1:]
        self.parsed_python += spacing + f'exec_out += {current_line}\n'
