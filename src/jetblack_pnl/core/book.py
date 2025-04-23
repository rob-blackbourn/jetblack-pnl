"""A book interface
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class IBook[Key](Protocol):
    """A book interface"""

    @property
    def key(self) -> Key:
        """The key for the book"""
