# pylint: disable=line-too-long
# pylint: disable=unnecessary-dunder-call
# pylint: disable=missing-module-docstring

from typing import List
from chiakilisp.models.token import Token
from chiakilisp.models.literal import Literal
from chiakilisp.models.expression import Expression


Node = Literal or Expression  # define the type for one node
Nodes = List[Node]  # define a type describing list of nodes


class Parser:

    """Parser is the class that takes a list of tokens and produces a wood of Expressions/Literals"""

    _wood: Nodes
    _tokens: List[Token]

    def __init__(self, tokens: List[Token]) -> None:

        """Initialize Parser instance"""

        self._tokens = tokens
        self._wood = []

    def wood(self) -> Nodes:

        """Its a getter for private _wood field"""

        return self._wood

    def parse(self) -> None:

        """Process a list of tokens in order to populate complete wood"""

        self._wood = read(self._tokens)  # utilizes dedicated read() func


def find_nearest_closing_paren(filtered: list, visited: list) -> tuple:

    """This function takes a token collection list and finds the nearest closing paren position"""

    _all = tuple(filter(lambda p: p not in visited and p[1].type() == Token.ClosingParen, filtered))
    if not _all:
        raise SyntaxError('Parser::find_nearest_closing_paren() there is no nearest ClosingParen token')
    return _all[0]


def find_nearest_opening_paren(filtered: list, visited: list) -> tuple:

    """This function takes a token collection list and finds the nearest opening paren position"""

    _all = tuple(filter(lambda p: p not in visited and p[1].type() == Token.OpeningParen, filtered))
    if not _all:
        raise SyntaxError('Parser::find_nearest_closing_paren() there is no nearest OpeningParen token')
    return _all[0]


def boundary(lst: List[Token]) -> int:

    """This function takes a token collection listing and finds actual boundary to starting expression"""

    assert len(lst) >= 2 and lst[0].type() == Token.OpeningParen  # non-empty tokens list, first should match '('.

    filtered: list  # for some reason, pylint confuses about filtered type assuming it's the same type as the list

    filtered = list(filter(lambda _pr: _pr[1].type() in [Token.OpeningParen, Token.ClosingParen], enumerate(lst)))

    starting_opening_paren = filtered[0]
    starting_opening_paren_position = starting_opening_paren[0]

    visited = []  # define list of paren tokens we've already visited

    while True:
        if not filtered:
            return -1  # return '-1' if there are no more paren tokens

        nearest_closing_paren = find_nearest_closing_paren(filtered, visited)
        nearest_closing_paren_position = nearest_closing_paren[0]

        reversed_filtered = list(reversed(filtered[:filtered.index(nearest_closing_paren) + 1]))

        nearest_opening_paren_to_that_closing = find_nearest_opening_paren(reversed_filtered, visited)
        nearest_opening_paren_to_that_closing_position = nearest_opening_paren_to_that_closing[0]

        if nearest_opening_paren_to_that_closing_position == starting_opening_paren_position:
            return nearest_closing_paren_position  # if matches exact same position, its valid expression boundary

        visited.append(nearest_closing_paren)
        visited.append(nearest_opening_paren_to_that_closing)  # then, append these two tokens to the visited list


def read(tokens: List[Token]) -> Nodes:

    """This function produces wood of Expressions/Literals"""

    if not tokens:
        return []  # allow empty expressions, useful for empty function parameters like: (defn my-function () ...)

    nodes: Nodes = []
    idx: int = 0
    is_inline_fn: bool = False
    is_commented: bool = False

    while idx < len(tokens):
        current_token = tokens[idx]
        if current_token.type() == Token.OpeningParen:  # <- if read() function has encountered OpeningParen token
            left_boundary, right_boundary = idx + 1, boundary(tokens[idx:]) + idx   # define expression boundaries
            if not is_commented:  # <----------------------- if current expression is not intended to be commented
                nodes.append(Expression(read(tokens[left_boundary:right_boundary]),    is_inline_fn=is_inline_fn))
            is_inline_fn = False  # <--------------------------------------- reset (previously set) inline fm flag
            is_commented = False  # <--------------------------------------- reset (previously set) commented flag
            idx = right_boundary + 1  # <--- and let the read() function to advance to the next one token instance
        elif current_token.type() == Token.InlineFunMarker:
            is_inline_fn = True  # <----------------------------------------------------------- set inline fn flag
            idx += 1  # <------------------- and let the read() function to advance to the next one token instance
        elif current_token.type() == Token.CommentedMarker:
            is_commented = True  # <----------------------------------------------------------- set commented flag
            idx += 1  # <------------------- and let the read() function to advance to the next one token instance
        else:
            if not is_commented:  # <-------------------------- if current literal is not intended to be commented
                nodes.append(Literal(current_token))  # <---------------------- then initialize and append literal
            is_inline_fn = False  # <--------------------------------------- reset (previously set) inline fm flag
            is_commented = False  # <--------------------------------------- reset (previously set) commented flag
            idx += 1  # <------------------- and let the read() function to advance to the next one token instance

    return nodes   # <----------------- so at the end of the day, return a list of Expression or Literal instances
