from .data.token import Token, Methods
from .helpers.str_helper import remove_quotes
from pathlib import Path
from typing import List


class Lexer:
    def __init__(self):
        ...

    def lex_file(self, file_path: Path | str) -> List[Token]:
        tokens = []
        if isinstance(file_path, str):
            file_path = Path(file_path)

        file_data: List[str] = file_path.read_text().split("\n")
        idx = 0
        using_bracket_finder = False
        while idx < len(file_data):
            line = file_data[idx]
            if "{{" not in line:
                tokens.append(Token(data=line, method=Methods.HTML))
                idx += 1
                continue

            l_bracket = line.find("{{")
            r_bracket = line.find("}}")

            # Add lines until the right bracket is found
            while r_bracket == -1:
                line += file_data[idx].strip(" ")
                r_bracket = line.find("}}")
                idx += 1
                using_bracket_finder = True

            # make it so that everything outside the brackets is also parsed
            tokens.append(Token(data=line[0:l_bracket], method=Methods.HTML))
            tokens.append(
                Token(data=line[r_bracket + 2: len(line)], method=Methods.HTML)
            )
            line = self.__filter_pyht(line=line[l_bracket + 2: r_bracket])

            tokens.append(self.get_token_by_line(line))

            if using_bracket_finder:
                using_bracket_finder = False
            else:
                idx += 1

        tokens.append(Token(data="EOF", method=Methods.EOF))
        return self.filter_tokens(tokens)

    def get_token_by_line(self, line):
        if line.startswith("include"):
            # NOTE: include will do the same as extends for the time being, however it might find use in the
            # future
            line = line[len("include"): len(line)]
            line = remove_quotes(line.replace(' ', ''))
            return Token(data=line, method=Methods.INCLUDE)
        elif line.startswith("extends"):
            # extending files means including its entire content and putting at the extends loc
            line = line[len("extends"): len(line)]
            line = remove_quotes(line.replace(' ', ''))
            return Token(data=line, method=Methods.EXTENDS)
        elif line.startswith("block"):
            # code blocks you can place anywhere
            line = line[len("block"): len(line)]
            line = remove_quotes(line.replace(' ', ''))
            return Token(data=line, method=Methods.BLOCK)
        elif line.startswith('='):
            # this is going to be for drawing python variables to the screen
            line = line[1: len(line)]
            return Token(data=line, method=Methods.VARIABLE)
        elif line == "pass":
            # makes spacing go back, so we can exit out of a for loop for example
            return Token(data='', method=Methods.PASS)
        elif line == "end":
            # the end block will do the same as the PASS block, this is just personal preference
            return Token(data='', method=Methods.END)
        else:
            return Token(data=line, method=Methods.PYTHON)

    def filter_tokens(self, tokens: List[Token]) -> List[Token]:
        index = 0
        while index < len(tokens):
            token = tokens[index]

            if token.method != Methods.HTML and token.method != Methods.PYTHON:
                index += 1
                continue

            filtered_data = token.data.replace(' ', '').replace('\n', '')
            if filtered_data == '' and len(filtered_data) == 0:
                tokens.pop(index)
                index -= 1
            index += 1

        return tokens

    def __filter_pyht(self, line: str):
        """
        filters all unnecessary data from line
        :param line: given in html file
        :return:
        """
        line = line.replace("{{", "").replace("}}", "")
        # removes all spaces at start of line
        return line.strip(" ")

