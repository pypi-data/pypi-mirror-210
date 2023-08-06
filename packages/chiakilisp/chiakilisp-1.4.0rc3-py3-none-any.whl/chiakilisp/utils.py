# pylint: disable=unreachable
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-return-statements  # it's fine. dear

from typing import Callable, Sized, Generator
from chiakilisp.proxies.keyword import Keyword

FORMATTERS = {'True': 'true', 'False': 'false',  'None': 'nil'}


def pairs(plain: Sized) -> Generator:

    """Returns generator of pairs;
    can fail if number of args is not even, check before"""

    return (plain[i:i + 2] for i in range(0, len(plain), 2))


def get_assertion_closure(e_object) -> Callable:

    """Returns the 'ASSERT()' function for the 'e_object'"""

    def ASSERT(where: tuple, condition, *args) -> None:
        """Helps to raise custom exception when asserting"""

        if not condition:
            msg, *rst = args
            where = ':'.join(map(str, where))
            raise e_object(
                f'{where} {e_object.__name__}: {msg}', *rst)

    return ASSERT  # <---- thus, return an assertion closure


def wrap(arg) -> str:

    """Wraps Python 3 object or instance to a string"""

    if isinstance(arg, Keyword):  # <-- wrap Keyword in a colon
        return f':{arg}'

    if isinstance(arg, str):  # <- wrap string in double quotes
        return f'"{arg}"'

    if callable(arg):  # if it's a callable object ...

        # ... get its custom name (for user defined functions);
        # in case it's an arbitrary Python 3 object (or class),
        # get its __name__ (or __class__.__name__)

        return getattr(
            arg, 'x__custom_name__x',
            getattr(
                arg, '__name__',
                getattr(arg, '__class__', None).__name__
            )
        )

    if isinstance(arg, set):  # if it's a set ...
        # then wrap its elements in {} and separate by a space

        formatted = ' '.join(map(wrap, arg))
        return f'#{{{formatted}}}'

    if isinstance(arg, list):  # if it's a list ...
        # then wrap its elements in [] and separate by a space

        formatted = ' '.join(map(wrap, arg))
        return f'[{formatted}]'

    if isinstance(arg, tuple):  # if it's a tuple ...
        # then wrap its elements in () and separate by a space

        formatted = ' '.join(map(wrap, arg))
        return f'({formatted})'

    if isinstance(arg, dict):  # if it's a dictionary ...
        # then wrap its elements in {} and separate by a space

        formatted = ' '.join(map(
            lambda _pair: f'{wrap(_pair[0])} {wrap(_pair[1])}',
            arg.items())
        )
        return f'{{{formatted}}}'

    if arg is ...:
        return '...'  # <---- print ...  for Ellipsis instances

    string = str(arg)  # <--- in other cases, cast it to string

    # try to apply custom formatting on a string representation
    return FORMATTERS.get(string, string)  # <- or return as is


def pprint(*args: list) -> None:

    """Pretty printer for any Python 3 object or instance"""

    # print() can take *args and print them separated by a
    # space character;
    # the reason we do it this way: we want to apply wrap()
    # function on each argument, compile a space character
    # separated string, then pass it to the print() function
    print(' '.join(map(wrap, args)))    # using map and join
