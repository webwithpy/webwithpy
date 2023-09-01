from pathlib import Path
from typing import List


class HtmlFile:
    def __init__(self, path: str | Path, encoding: str = 'utf-8'):
        self.path = path
        self.encoding = encoding

        if isinstance(self.path, str):
            self.path = Path(self.path).expanduser()
            if not self.path.exists():
                raise FileNotFoundError(f"Couldn't find html file at {self.path}")

        self.html_py_content: list[str] = self.path.read_text(encoding=self.encoding).split('\n')

    def render(self) -> str:
        exec_out = ''
        parser = HtmlParser(exec_out_name="exec_out")
        parsed_html_code = parser.render(self.html_py_content)

        lvars = {'self': self, 'exec_out': exec_out}
        exec(parsed_html_code, globals(), lvars)

        return exec_out


class HtmlParser:
    def __init__(self, exec_out_name: str):
        self.parsed_python = ''
        # the name of the variable in locals
        # see HtmlFile.render
        self.exec_out_name = exec_out_name

    def render(self, html_py_content: List[str]) -> str:
        spacing = ''

        for line in html_py_content:
            current_line = line.strip(' ')

            if '{{=' in line:
                self.__draw_var(spacing, current_line)
            elif '{{pass' in line:
                spacing = spacing[:-4]
            elif '{{' in line:
                self.__render_python(spacing, current_line)

        return self.parsed_python

    def __render_python(self, spacing: str, line: str) -> None:
        current_line = line[2:-2]

        if current_line == 'pass':
            spacing = spacing[:-4]

        self.parsed_python += spacing + current_line + "\n"

        if ':' in current_line:
            spacing += '    '

    def __draw_var(self, spacing: str, line: str) -> None:
        current_line = line[3:-2]
        self.parsed_python += spacing + f'exec_out += {current_line}\n'
