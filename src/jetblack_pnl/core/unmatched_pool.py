"""An interface for an unmatched pool.
"""

from typing import Protocol, Sequence, runtime_checkable

from .split_trade import SplitTrade


@runtime_checkable
class IUnmatchedPool[TradeKey, Context](Protocol):  # type: ignore
    """A pool of unmatched trades"""

    def append(
            self,
            opening: SplitTrade[TradeKey],
            context: Context
    ) -> None:
        ...

    def insert(
            self,
            opening: SplitTrade[TradeKey],
            context: Context
    ) -> None:
        ...

    def pop(
            self,
            closing: SplitTrade[TradeKey],
            context: Context
    ) -> SplitTrade[TradeKey]:
        ...

    def has(
            self,
            closing: SplitTrade[TradeKey],
            context: Context
    ) -> bool:
        ...

    def pool(self, context: Context) -> Sequence[SplitTrade[TradeKey]]:
        ...
