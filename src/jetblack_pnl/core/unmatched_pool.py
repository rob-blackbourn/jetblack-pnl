"""An interface for an unmatched pool.
"""

from typing import Protocol, runtime_checkable

from .split_trade import SplitTrade


@runtime_checkable
class IUnmatchedPool(Protocol):
    """A pool of unmatched trades"""

    def append(self, opening: SplitTrade) -> None:
        ...

    def insert(self, opening: SplitTrade) -> None:
        ...

    def pop(self, closing: SplitTrade) -> SplitTrade:
        ...

    def has(self, closing: SplitTrade) -> bool:
        ...
