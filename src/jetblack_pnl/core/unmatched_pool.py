"""An interface for an unmatched pool.
"""

from typing import Protocol, Sequence, runtime_checkable

from .split_trade import SplitTrade
from .trade import ITrade


@runtime_checkable
class IUnmatchedPool[TradeT: ITrade, ContextT](Protocol):  # type: ignore
    """A pool of unmatched trades"""

    def append(
            self,
            opening: SplitTrade[TradeT],
            context: ContextT
    ) -> None:
        ...

    def insert(
            self,
            opening: SplitTrade[TradeT],
            context: ContextT
    ) -> None:
        ...

    def pop(
            self,
            closing: SplitTrade[TradeT],
            context: ContextT
    ) -> SplitTrade[TradeT]:
        ...

    def has(
            self,
            closing: SplitTrade[TradeT],
            context: ContextT
    ) -> bool:
        ...

    def pool(self, context: ContextT) -> Sequence[SplitTrade[TradeT]]:
        ...
