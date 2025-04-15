"""A simple implementation of a book"""

from ...core import IBook


class Book(IBook[str]):
    """A simple implementation of a book"""

    def __init__(self, key: str) -> None:
        self._key = key

    @property
    def key(self) -> str:
        return self._key
