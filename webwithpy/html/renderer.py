from webwithpy.routing.router import Router

from .data.ast import Block, Stmt, Include, Extends, Python, Html, Variable, Request
from .parser import DefaultParser
from .lexer import Lexer
from typing import List


class RenderBlock:
    def __init__(self, code: str):
        self.code = code


class DefaultRenderer:
    blocks = {}
    code = ""
    spacing = ""

    @classmethod
    def generate_pre_code(cls, program: List[Stmt], spacing: str = "", **kwargs) -> str:
        # we might need to start with diff spacing for fast impl
        if len(spacing) > 0:
            cls.spacing = spacing

        for index, stmt in enumerate(program):
            match stmt.kind:
                case "block":
                    stmt: Block
                    copied_code = cls.code
                    copied_spacing = cls.spacing
                    cls.code = cls.spacing = ""

                    block_code = cls.generate_pre_code(stmt.block_data, **kwargs)

                    cls.blocks[stmt.name] = block_code
                    cls.code, cls.spacing = [copied_code, copied_spacing]
                case "extends":
                    stmt: Extends
                    # simply render file and include it into the program
                    cls.__render_at_file_path(file_path=stmt.file_path, **kwargs)
                case "include":
                    stmt: Include
                    cls.__render_at_file_path(file_path=stmt.file_path, **kwargs)
                case "variable":
                    stmt: Variable | Block
                    # stmt.code is in this case the name of the block.
                    if stmt.code in cls.blocks:
                        lines = cls.blocks[stmt.code].split("\n")
                        for line in lines:
                            cls.code += f"{cls.spacing}{line}\n"
                    else:
                        stmt.code = f"str({stmt.code})"

                        cls.code += f"{cls.spacing}html += {stmt.code}\n"
                case "request":
                    stmt: Request
                    result, _, _ = Router._call_func_by_route(stmt.request_path, "GET")
                    cls.code += f"{cls.spacing}html += str({result})\n"
                case "python":
                    if "else" in stmt.code or "elif" in stmt.code:
                        cls.spacing = cls.spacing[:-4]
                    stmt: Python
                    cls.code += f"{cls.spacing}{stmt.code}\n"
                    if ":" in stmt.code:
                        cls.spacing += "    "
                case "html":
                    stmt: Html
                    stmt.code = stmt.code.replace('"', "'")
                    cls.code += f'{cls.spacing}html += "{stmt.code}"\n'
                case "pass":
                    cls.spacing = cls.spacing[:-4]

        code = cls.code
        cls.code = ""
        return code

    @classmethod
    def render(cls, program: List[Stmt], **kwargs) -> str:
        code = cls.generate_pre_code(program=program, **kwargs)
        kwargs["html"] = ""
        kwargs["RenderBlock"] = RenderBlock
        exec(code, {}, kwargs)

        return kwargs["html"]

    @classmethod
    def render_pre(cls, code, **kwargs):
        kwargs["html"] = ""
        kwargs["RenderBlock"] = RenderBlock
        exec(code, {}, kwargs)

        return kwargs["html"]

    @classmethod
    def __render_at_file_path(cls, file_path: str, **kwargs) -> None:
        """
        when a file is for example extended we will need to parse that one too.
        the rendered python will be placed where the extends happens
        :param file_path: path of the file
        :return:
        """
        lexer = Lexer()
        tokens = lexer.lex_file(file_path)
        parser = DefaultParser(tokens)

        program = parser.parse()

        code = DefaultRenderer.generate_pre_code(program, **kwargs)
        cls.code = code
