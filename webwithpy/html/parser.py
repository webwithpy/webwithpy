from .data.ast import Variable, Python, Html, Block, Include, Extends, Pass, End
from .data.token import Methods, Token
from .helpers.str_helper import remove_quotes
from .helpers.exceptions import UnexpectedStmt
from typing import List


class DefaultParser:
    def __init__(self, tokens: List[Token]):
        self.program = []
        self.tokens = tokens

    def at(self) -> Token:
        return self.tokens[0]

    def eat(self) -> Token:
        return self.tokens.pop(0)

    def isEOF(self):
        return self.at().method == Methods.EOF

    def parse(self):
        while not self.isEOF():
            self.program.append(self._parse_func())

        return self.program

    def _parse_func(self):
        if self.at().method == Methods.BLOCK:
            block_name = self.eat().data
            block_data = []
            while self.at().method != Methods.END:
                block_data.append(self._parse_func())
            self.eat()
            return Block(block_name=block_name, data=block_data)
        elif self.at().method == Methods.EXTENDS:
            file_path = remove_quotes(self.eat().data)
            extends = Extends(file_path=file_path)
            return extends
        elif self.at().method == Methods.INCLUDE:
            file_path = remove_quotes(self.eat().data)
            include = Include(file_path=file_path)
            return include
        elif self.at().method == Methods.PASS:
            self.eat()
            return Pass()
        else:
            return self._parse_py()

    def _parse_py(self):
        if self.at().method == Methods.PYTHON:
            return Python(code=self.eat().data)
        elif self.at().method == Methods.VARIABLE:
            return Variable(code=self.eat().data)
        else:
            return self._parse_html()

    def _parse_html(self):
        if self.at().method == Methods.HTML:
            return Html(code=self.eat().data)
        else:
            raise UnexpectedStmt(self.at())
