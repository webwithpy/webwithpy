from dataclasses import dataclass
from enum import IntEnum, auto


class Methods(IntEnum):
    HTML = auto()
    INCLUDE = auto()
    EXTENDS = auto()
    BLOCK = auto()
    VARIABLE = auto()
    PYTHON = auto()
    END = auto()
    PASS = auto()
    EOF = auto()


@dataclass
class Token:
    data: str
    method: int

    def __str__(self):
        return f"({self.data}: {self.method})"

    def __repr__(self):
        return self.__str__()
