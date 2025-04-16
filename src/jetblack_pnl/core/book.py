"""A book interface
"""

from typing import Protocol, TypeVar


TBookKey = TypeVar('TBookKey', covariant=True)


class IBook(Protocol[TBookKey]):
    """A book interface"""

    @property
    def key(self) -> TBookKey:
        """The key for the book"""
