from pathlib import Path


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
        self.content = ''
        parsed_python = ""
        spacing = ""

        for line in self.html_py_content:
            line = line.strip(' ')

            # line is python code
            if '{{' in line:
                line = line[line.find('{{')+2:line.find('}}')]

                if line[0] != '=':
                    if line == 'pass':
                        spacing = spacing[0:len(spacing) - 4]

                    parsed_python += spacing + line + "\n"
                    if ':' in line:
                        spacing += '    '
                    continue
                else:
                    line = line[1:len(line)]
                    parsed_python += spacing + f'self.content += {line}\n'
                    continue

            parsed_python += spacing + f'self.content += "{line}"\n'

        lvars = {'self': self, 'self.content': self.content}
        exec(parsed_python, globals(), lvars)

        return self.content
