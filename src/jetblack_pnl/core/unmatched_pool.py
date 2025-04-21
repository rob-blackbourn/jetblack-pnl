"""An interface for an unmatched pool.
"""

from typing import Protocol, runtime_checkable

from .context import TContext
from .split_trade import SplitTrade
from .trade import TTradeKey


@runtime_checkable
class IUnmatchedPool(Protocol[TTradeKey, TContext]):  # type: ignore
    """A pool of unmatched trades"""

    def append(
            self,
            opening: SplitTrade[TTradeKey],
            context: TContext
    ) -> None:
        ...

    def insert(
            self,
            opening: SplitTrade[TTradeKey],
            context: TContext
    ) -> None:
        ...

    def pop(
            self,
            closing: SplitTrade[TTradeKey],
            context: TContext
    ) -> SplitTrade[TTradeKey]:
        ...

    def has(
            self,
            closing: SplitTrade[TTradeKey],
            context: TContext
    ) -> bool:
        ...
