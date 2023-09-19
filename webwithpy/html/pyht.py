from .helpers.string_helper import filter_pyht_line, remove_quotes
from pathlib import Path
from typing import List, Any
from os import PathLike
from dataclasses import dataclass


class HtmlFile:
    def __init__(self, path: str | Path, encoding: str = "utf-8"):
        self.path = path
        self.encoding = encoding

        if isinstance(self.path, str):
            self.path = Path(self.path).expanduser()
            if not self.path.exists():
                raise FileNotFoundError(f"Couldn't find html file at {self.path}")

        self.html_py_content: list[str] = self.path.read_text(
            encoding=self.encoding
        ).split("\n")

    def render(self, exec_vars: Any) -> str:
        exec_out = ""
        parser = HtmlParser(html_file_name=self.path.name)
        parsed_html_code = parser.render(self.html_py_content)
        lvars = {"exec_out": exec_out}

        if isinstance(exec_vars, dict):
            lvars.update(exec_vars)
        else:
            lvars["vars"] = exec_vars

        exec(parsed_html_code, globals(), lvars)

        return lvars["exec_out"]


class HtmlParser:
    def __init__(self, html_file_name: str):
        self.parts = []
        self.html_file_name = html_file_name
        self.extends_path: Path | PathLike = None

    def render(self, html_py_content: List[str]) -> str | List:
        spacing = ""

        for line_index, unfiltered_line in enumerate(html_py_content):
            filtered_line = filter_pyht_line(unfiltered_line)

            if len(filtered_line) == 0 or "{{" not in unfiltered_line:
                continue
            elif filtered_line == "end":
                return self.parts

            if filtered_line.startswith("="):
                self.__draw_var(spacing, filtered_line)
            elif filtered_line == "pass":
                spacing = spacing[:-4]
            elif filtered_line.startswith("extends "):
                self.__parse_extends(filtered_line)
            elif filtered_line.startswith("block "):
                current_line = filtered_line.removeprefix("block ")
                block_name = remove_quotes(current_line)
                parts_copy = self.parts.copy()
                self.parts = []
                if (block_index := self.__block_index(block_name)) != -1:

                    self.parts[block_index] = Block(block_name=block_name)
                else:
                    ...
            elif filtered_line == "include":
                ...
            else:
                self.__render_python(spacing, filtered_line)
                if filtered_line[-1] == ":":
                    spacing += "    "

        if spacing != "":
            raise IndentationError(
                f"The html file {self.html_file_name} cannot be rendered due to a indentation error."
                "\n(you probably forgot to add a `{{pass}}` to the code)"
            )

        if self.extends_path:
            extends_parser = HtmlParser(self.extends_path.name)
            file_text = self.extends_path.read_text(encoding="utf-8").split("\n")

            parts: List = extends_parser.render(file_text)
            return "".join(parts + self.parts)

        return "".join(self.parts)

    def __render_python(self, spacing: str, line: str) -> None:
        self.parts.append(spacing + line + "\n")

    def __draw_var(self, spacing: str, line: str) -> None:
        current_line = line[1:]
        self.parts.append(spacing + f"exec_out += {current_line}\n")

    def __parse_extends(self, line: str):
        current_line = line.removeprefix("extends")
        current_line = remove_quotes(current_line)
        file_path = Path(current_line)
        self.extends_path = file_path

    def __block_index(self, name: str) -> int:
        """
        function finds the index of a block in the list self.parts by the given name
        """
        for index, part in enumerate(self.parts):
            if isinstance(part, Block) and part.block_name == name:
                return index
        return -1

    def __find_end_idx(self, lines: List[str]):
        """
        find the block {{end}} in an html_file(list[str])
        """
        for index, line in enumerate(lines):
            if "{{end}}" in line:
                return index
        raise NameError("Error, Please close all blocks with {{end}}!")

@dataclass
class Block:
    # name of the block
    block_name: str
    # content of the block
    block_content: str
    # all content before this block
    prev_content: str

    def get_content(self):
        return self.prev_content + self.block_content