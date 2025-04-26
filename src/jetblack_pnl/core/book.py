"""A book interface
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class IBook[KeyT](Protocol):
    """A book interface"""

    @property
    def key(self) -> KeyT:
        """The key for the book"""
