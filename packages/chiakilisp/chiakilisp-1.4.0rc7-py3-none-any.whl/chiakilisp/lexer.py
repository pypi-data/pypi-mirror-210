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

    def _raise_syntax_error(self, message: str) -> None:

        """A shortcut for future that helps to throw a SyntaxError"""

        raise SyntaxError(f'{":".join(map(str, self.pos()))}: {message}')

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

        while self._can_be_advanced():

            if self._current_char_is_semicolon() or \
                    (self._current_char_is_hash() and
                        self._next_char_is_exclamation_mark()):
                self._advance()
                while self._can_be_advanced():
                    if self._current_char_is_nl():
                        break
                    self._advance()
                self._advance()
                self._increment_line_number_with_char_number_reset()

            elif (self._current_char_is_hash()
                  and self._next_char_is_opening_paren()):
                self._advance()
                self._increment_char_number()
                self._tokens.append(Token(Token.InlineFunMarker,  '#{', self.pos()))

            elif (self._current_char_is_hash()
                  and self._next_char_is_underscore()):
                self._advance()
                self._advance()
                self._increment_char_number()
                self._increment_char_number()
                self._tokens.append(Token(Token.CommentedMarker,  '#_', self.pos()))

            elif (self._current_char_is_hash()
                  and self._next_char_is_cr_opening_paren()):
                self._advance()
                self._increment_char_number()  # <-- increment character num as well
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,    'setty', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif (self._current_char_is_hash()
                  and self._next_char_is_sq_opening_paren()):
                self._advance()
                self._increment_char_number()  # <-- increment character num as well
                self._tokens.append(Token(Token.OpeningParen,     '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,   'tuply', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_number() \
                    or (self._current_char_is_sign()
                        and self._next_char_is_number()):
                value = self._current_char()
                self._advance()
                self._increment_char_number()
                while self._can_be_advanced():
                    if self._current_char_is_number() \
                            or self._current_char_is_dot():
                        value += self._current_char()
                        self._advance()
                        self._increment_char_number()
                    else:
                        break
                if re.match(r'^\d+?\.{2}(\d+)?$', value):
                    self._tokens.append(Token(Token.Slice, value, self.pos()))
                elif re.match(r'^(-)?\d+(\.\d+)?$', value):
                    self._tokens.append(Token(Token.Number, value, self.pos()))
                else:
                    self._raise_syntax_error(f'Invalid float syntax: {value}.')

            elif self._current_char_is_letter() \
                    or self._current_char_is_colon():
                value = self._current_char()
                self._advance()
                self._increment_char_number()
                while self._can_be_advanced():
                    if self._current_char_is_letter() or \
                            self._current_char_is_number():
                        value += self._current_char()
                        self._advance()
                        self._increment_char_number()
                    else:
                        break
                if re.match(r'^\.\d+$', value):
                    value = '0' + value  # make it possible to define 0.2 as .2
                    self._tokens.append(Token(Token.Number, value, self.pos()))
                elif re.match(r'^-\.\d+$', value):
                    value = '-0' + value[1:]  # make it possible to prepend '-'
                    self._tokens.append(Token(Token.Number, value, self.pos()))
                elif value.startswith(':'):
                    self._tokens.append(Token(Token.Keyword, value, self.pos()))
                elif value == 'nil':
                    self._tokens.append(Token(Token.Nil, value, self.pos()))
                elif value in ['true', 'false']:
                    self._tokens.append(Token(Token.Boolean, value, self.pos()))
                elif re.match(r'^\.{2}\d+$', value):  # make it equivalent for 0..2
                    self._tokens.append(Token(Token.Slice, value, self.pos()))
                else:
                    self._tokens.append(Token(Token.Identifier, value, self.pos()))

            elif self._current_char_is_double_quote():
                value = ''
                while self._can_be_advanced():
                    self._advance()
                    self._increment_char_number()
                    if self._current_char() == '\\':
                        self._advance()
                        self._increment_char_number()
                        if self._current_char() == 'n':
                            value += '\n'
                        if self._current_char() == 't':
                            value += '\t'
                        if self._current_char_is_double_quote():
                            value += '"'
                        continue
                    if not self._current_char_is_double_quote():
                        value += self._current_char()
                    else:
                        self._tokens.append(Token(Token.String, value,  self.pos()))
                        break
                self._advance()  # <--- call _advance() to skip the leading '"' char
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_opening_paren():
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_closing_paren():
                self._tokens.append(Token(Token.ClosingParen,      ')', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_cr_opening_paren():
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,    'dicty', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_cr_closing_paren():
                self._tokens.append(Token(Token.ClosingParen,      ')', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_sq_opening_paren():
                self._tokens.append(Token(Token.OpeningParen,      '(', self.pos()))
                self._tokens.append(Token(Token.Identifier,    'listy', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_sq_closing_paren():
                self._tokens.append(Token(Token.ClosingParen,      ')', self.pos()))
                self._advance()
                self._increment_char_number()  # <-- increment character num as well

            elif self._current_char_is_nl():
                self._advance()
                self._increment_line_number_with_char_number_reset()  # go a newline

            else:
                self._advance()  # call _advance() to skip over the extra characters
                self._increment_char_number()  # <-- increment character num as well

    def _advance(self) -> None:

        """Advances char pointer"""

        self._pointer += 1

    def _current_char(self) -> str:

        """Returns a current character"""

        return self._source_code[self._pointer]

    def _next_char(self) -> str:

        """Returns a next character if possible, otherwise ''"""

        if (len(self._source_code) == 1 and not self._pointer) \
                or not self._can_be_advanced():
            return ''
        return self._source_code[self._pointer + 1]

    def _can_be_advanced(self) -> bool:

        """Whether source has a next character"""

        return self._pointer < len(self._source_code)

    def _current_char_is_nl(self) -> bool:

        """Returns whether current character is a newline character"""

        return self._current_char() == '\n'

    def _current_char_is_sign(self) -> bool:

        """Returns whether current character is a number sign: +, -"""

        return self._current_char() in ['+', '-']

    def _current_char_is_hash(self) -> bool:

        """Returns whether current character is a hashtag character"""

        return self._current_char() == '#'

    def _current_char_is_dot(self) -> bool:

        """Returns whether current character is a dot character"""

        return self._current_char() == '.'

    def _current_char_is_colon(self) -> bool:

        """Returns whether current character is a colon character"""

        return self._current_char() == ':'

    def _current_char_is_semicolon(self) -> bool:

        """Returns whether current character is a semicolon character"""

        return self._current_char() == ';'

    def _current_char_is_double_quote(self) -> bool:

        """Returns whether current character is a double-quote character"""

        return self._current_char() == '"'

    def _current_char_is_opening_paren(self) -> bool:

        """Returns whether current character is an opening paren character"""

        return self._current_char() == '('

    def _current_char_is_closing_paren(self) -> bool:

        """Returns whether current character is a closing paren character"""

        return self._current_char() == ')'

    def _current_char_is_cr_opening_paren(self) -> bool:

        """Returns whether current character is a curly-opening paren character"""

        return self._current_char() == '{'

    def _current_char_is_cr_closing_paren(self) -> bool:

        """Returns whether current character is a curly-closing paren character"""

        return self._current_char() == '}'

    def _current_char_is_sq_opening_paren(self) -> bool:

        """Returns whether current character is a square-opening paren character"""

        return self._current_char() == '['

    def _current_char_is_sq_closing_paren(self) -> bool:

        """Returns whether current character is a square-closing paren character"""

        return self._current_char() == ']'

    def _next_char_is_number(self) -> bool:

        """Returns whether next symbol is a character, valid number is from 0 to 9"""

        return re.match(r'\d', self._next_char()) is not None

    def _next_char_is_exclamation_mark(self) -> bool:

        """Returns whether next character is an exclamation mark character"""

        return self._next_char() == '!'

    def _next_char_is_opening_paren(self) -> bool:

        """Returns whether next character is an opening paren character"""

        return self._next_char() == '('

    def _next_char_is_underscore(self) -> bool:

        """Returns whether next character is an underscore character"""

        return self._next_char() == '_'

    def _next_char_is_cr_opening_paren(self) -> bool:

        """Returns whether next character is a curly-opening paren character"""

        return self._next_char() == '{'

    def _next_char_is_sq_opening_paren(self) -> bool:

        """Returns whether next character is a square-opening paren character"""

        return self._next_char() == '['

    def _current_char_is_number(self) -> bool:

        """Returns whether current character is a number, valid number is from 0 to 9"""

        return re.match(r'\d', self._current_char()) is not None

    def _current_char_is_letter(self) -> bool:

        """Returns whether current character is a letter: valid letter is from a-zA-Z or from ALPHABET"""

        return re.match(r'[a-zA-Z]', self._current_char()) is not None or self._current_char() in ALPHABET
