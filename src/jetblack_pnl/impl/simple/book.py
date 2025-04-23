"""A simple implementation of a book"""

from ...core import IBook

from .types import BookKey


class Book(IBook[BookKey]):
    """A simple implementation of a book"""

    def __init__(self, key: BookKey) -> None:
        self._key = key

    @property
    def key(self) -> BookKey:
        return self._key
