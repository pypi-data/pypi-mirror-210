# pylint: disable=fixme
# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring

import re
from typing import List
from chiakilisp.models.token import Token  # Lexer returns a Token instances list


ALPHABET = ['+', '-', '*', '/', '=', '<', '>', '?', '!', '.', '_', '&', ':', '%']


class Lexer:

    """
    Lexer is the class that takes the source code, then produces a list of tokens
    """

    _source_code: str  # <----------------------------------- source code context
    _source_code_file_name: str  # <----------------------- source code file name
    _pointer: int = 0  # <------------------------------ default pointer position
    _tokens: List[Token]  # <----------------------- list of the populated Tokens
    _line_num, _char_num = 1, 0  # <------------ initial pointer position in file

    def __init__(self, source_code: str, source_code_file_name: str) -> None:

        """Initialize Lexer instance"""

        self._source_code = source_code
        self._source_code_file_name = source_code_file_name
        self._tokens = []

    def tokens(self) -> List[Token]:

        """Returns list of tokens"""

        return self._tokens

    def _increment_char_number(self) -> None:

        """Increments character number by 1"""

        self._char_num += 1

    def _increment_line_number_with_char_number_reset(self) -> None:

        """Increments line number by 1 and resets character number"""

        self._char_num = 0
        self._line_num += 1

    def pos(self) -> tuple:

        """Returns a tuple containing current char and line number"""

        return tuple((self._source_code_file_name, self._line_num, self._char_num))

    def lex(self) -> None:  # pylint: disable=R0912, disable=R0915  # maybe refactor

        """Process the given source code, thus produces a list of Token instances"""

        while self._has_next_symbol():

            if self._current_symbol_is_semicolon() or \
                    (self._current_symbol_is_hash() and
                        self._next_symbol_is_exclamation_mark()):
                self._advance()
                while self._has_next_symbol():
                    if self._current_symbol_is_nl():
                        break
                    self._advance()
                self._advance()
                self._increment_line_number_with_char_number_reset()

            elif (self._current_symbol_is_hash()
                    and self._next_symbol_is_opening_paren()):
                self._advance()
                self._increment_char_number()
                self._tokens.append(Token(Token.InlineFunMarker,  '#{', self.pos()))

            elif (self._current_symbol_is_hash()
                    and self._next_symbol_is_underscore()):
                self._advance()
                self._advance()
                self._increment_char_number()
                self._increment_char_number()
                self._tokens.append(Token(Token.CommentedMarker,  '#_', self.pos()))

            elif (self._current_symbol_is_hash()
                    and self._next_symbol_is_cr_opening_paren()):
                self._advance()
                self._increment_char_number()  # <-- increment character num as well
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,    'setty', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif (self._current_symbol_is_hash()
                  and self._next_symbol_is_sq_opening_paren()):
                self._advance()
                self._increment_char_number()  # <-- increment character num as well
                self._tokens.append(Token(Token.OpeningParen,     '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,   'tuply', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_number() \
                    or (self._current_symbol_is_sign()
                        and self._next_symbol_is_number()):
                has_already_encountered_dot_character = False
                value = self._current_symbol()
                self._advance()
                self._increment_char_number()
                while self._has_next_symbol():
                    if self._current_symbol_is_number() or \
                            (self._current_symbol_is_dot() and
                             not has_already_encountered_dot_character):
                        if self._current_symbol_is_dot():
                            has_already_encountered_dot_character = True
                        value += self._current_symbol()
                        self._advance()
                        self._increment_char_number()
                    else:
                        break
                self._tokens.append(Token(Token.Number, value, self.pos()))

            elif self._current_symbol_is_letter() \
                    or self._current_symbol_is_colon():
                value = self._current_symbol()
                self._advance()
                self._increment_char_number()
                while self._has_next_symbol():
                    if self._current_symbol_is_letter() or \
                            self._current_symbol_is_number():
                        value += self._current_symbol()
                        self._advance()
                        self._increment_char_number()
                    else:
                        break
                if value.startswith(':'):
                    self._tokens.append(Token(Token.Keyword, value, self.pos()))
                elif value == 'nil':
                    self._tokens.append(Token(Token.Nil, value, self.pos()))
                elif value in ['true', 'false']:
                    self._tokens.append(Token(Token.Boolean, value, self.pos()))
                else:
                    self._tokens.append(Token(Token.Identifier, value, self.pos()))

            elif self._current_symbol_is_double_quote():
                value = ''
                while self._has_next_symbol():
                    self._advance()
                    self._increment_char_number()
                    if self._current_symbol() == '\\':
                        self._advance()
                        self._increment_char_number()
                        if self._current_symbol() == 'n':
                            value += '\n'
                        if self._current_symbol() == 't':
                            value += '\t'
                        if self._current_symbol_is_double_quote():
                            value += '"'
                        continue
                    if not self._current_symbol_is_double_quote():
                        value += self._current_symbol()
                    else:
                        self._tokens.append(Token(Token.String, value,  self.pos()))
                        break
                self._advance()  # <--- call _advance() to skip the leading '"' char
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_opening_paren():
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_closing_paren():
                self._tokens.append(Token(Token.ClosingParen,      ')', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_cr_opening_paren():
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,    'dicty', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_cr_closing_paren():
                self._tokens.append(Token(Token.ClosingParen,      ')', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_sq_opening_paren():
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,    'listy', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_sq_closing_paren():
                self._tokens.append(Token(Token.ClosingParen,      ')', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_symbol_is_nl():
                self._advance()
                self._increment_line_number_with_char_number_reset()  # go a newline

            else:
                self._advance()  # call _advance() to skip over the extra characters
                self._increment_char_number()  # <-- increment character num as well

    def _advance(self) -> None:

        """Advance the pointer"""

        self._pointer += 1

    def _current_symbol(self) -> str:

        """Returns the current symbol"""

        return self._source_code[self._pointer]

    def _next_symbol(self) -> str:

        """Returns the next symbol (if possible, otherwise '')"""

        if (len(self._source_code) == 1 and not self._pointer) \
                or not self._has_next_symbol():
            return ''
        return self._source_code[self._pointer + 1]

    def _has_next_symbol(self) -> bool:

        """Returns whether source has next symbol"""

        return self._pointer < len(self._source_code)

    def _current_symbol_is_nl(self) -> bool:

        """Returns whether current symbol is a newline symbol"""

        return self._current_symbol() == '\n'

    def _current_symbol_is_sign(self) -> bool:

        """Returns whether current symbol is a number sign"""

        return self._current_symbol() in ['+', '-']

    def _current_symbol_is_hash(self) -> bool:

        """Returns whether current symbol is a hashtag symbol"""

        return self._current_symbol() == '#'

    def _current_symbol_is_dot(self) -> bool:

        """Returns whether current symbol is a dot symbol"""

        return self._current_symbol() == '.'

    def _current_symbol_is_colon(self) -> bool:

        """Returns whether current symbol is a colon symbol"""

        return self._current_symbol() == ':'

    def _current_symbol_is_semicolon(self) -> bool:

        """Returns whether current symbol is a semicolon symbol"""

        return self._current_symbol() == ';'

    def _current_symbol_is_double_quote(self) -> bool:

        """Returns whether current symbol is a double-quote symbol"""

        return self._current_symbol() == '"'

    def _current_symbol_is_opening_paren(self) -> bool:

        """Returns whether current symbol is an opening paren symbol"""

        return self._current_symbol() == '('

    def _current_symbol_is_closing_paren(self) -> bool:

        """Returns whether current symbol is a closing paren symbol"""

        return self._current_symbol() == ')'

    def _current_symbol_is_cr_opening_paren(self) -> bool:

        """Returns whether current symbol is a curly-opening paren symbol"""

        return self._current_symbol() == '{'

    def _current_symbol_is_cr_closing_paren(self) -> bool:

        """Returns whether current symbol is a curly-closing paren symbol"""

        return self._current_symbol() == '}'

    def _current_symbol_is_sq_opening_paren(self) -> bool:

        """Returns whether current symbol is a square-opening paren symbol"""

        return self._current_symbol() == '['

    def _current_symbol_is_sq_closing_paren(self) -> bool:

        """Returns whether current symbol is a square-closing paren symbol"""

        return self._current_symbol() == ']'

    def _next_symbol_is_number(self) -> bool:

        """Returns whether next symbol is a number, valid number is from 0 to 9"""

        return re.match(r'\d', self._next_symbol()) is not None

    def _next_symbol_is_exclamation_mark(self) -> bool:

        """Returns whether next symbol is an exclamation mark symbol"""

        return self._next_symbol() == '!'

    def _next_symbol_is_opening_paren(self) -> bool:

        """Returns whether next symbol is an opening paren symbol"""

        return self._next_symbol() == '('

    def _next_symbol_is_underscore(self) -> bool:

        """Returns whether next symbol is an underscore symbol"""

        return self._next_symbol() == '_'

    def _next_symbol_is_cr_opening_paren(self) -> bool:

        """Returns whether next symbol is a curly-opening paren symbol"""

        return self._next_symbol() == '{'

    def _next_symbol_is_sq_opening_paren(self) -> bool:

        """Returns whether next symbol is a square-opening paren symbol"""

        return self._next_symbol() == '['

    def _current_symbol_is_number(self) -> bool:

        """Returns whether current symbol is a number, valid number is from 0 to 9"""

        return re.match(r'\d', self._current_symbol()) is not None

    def _current_symbol_is_letter(self) -> bool:

        """Returns whether current symbol is a letter: valid letter is from a-zA-Z or from the alphabet"""

        return re.match(r'[a-zA-Z]', self._current_symbol()) is not None or self._current_symbol() in ALPHABET
