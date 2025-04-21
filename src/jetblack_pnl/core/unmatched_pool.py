"""An interface for an unmatched pool.
"""

from typing import Protocol, runtime_checkable

from .split_trade import SplitTrade
from .trade import TTradeKey


@runtime_checkable
class IUnmatchedPool(Protocol[TTradeKey]):
    """A pool of unmatched trades"""

    def append(self, opening: SplitTrade[TTradeKey]) -> None:
        ...

    def insert(self, opening: SplitTrade[TTradeKey]) -> None:
        ...

    def pop(self, closing: SplitTrade[TTradeKey]) -> SplitTrade[TTradeKey]:
        ...

    def has(self, closing: SplitTrade[TTradeKey]) -> bool:
        ...
