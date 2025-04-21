"""A book interface
"""

from typing import Protocol, TypeVar, runtime_checkable


TBookKey = TypeVar('TBookKey', covariant=True)


@runtime_checkable
class IBook(Protocol[TBookKey]):
    """A book interface"""

    @property
    def key(self) -> TBookKey:
        """The key for the book"""
