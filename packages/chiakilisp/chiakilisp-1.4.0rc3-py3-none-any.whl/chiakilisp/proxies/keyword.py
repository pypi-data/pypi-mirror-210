"""The Keyword proxy class implementation"""


class Keyword(str):

    """Keyword Proxy Class based on `str`"""

    def __new__(cls, raw: str) -> 'Keyword':

        return super().__new__(cls, raw[1:])
