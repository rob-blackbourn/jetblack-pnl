"""An interface for an unmatched pool.
"""

from typing import Protocol

from .split_trade import SplitTrade
from .trade import TTradeData


class IUnmatchedPool(Protocol[TTradeData]):
    """A pool of unmatched trades"""

    def append(self, opening: SplitTrade[TTradeData]) -> None:
        ...

    def insert(self, opening: SplitTrade[TTradeData]) -> None:
        ...

    def pop(self, closing: SplitTrade[TTradeData]) -> SplitTrade[TTradeData]:
        ...

    def has(self, closing: SplitTrade[TTradeData]) -> bool:
        ...
