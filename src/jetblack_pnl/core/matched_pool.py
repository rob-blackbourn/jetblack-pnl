"""An interface for a matched pool.
"""

from typing import Protocol, Sequence, runtime_checkable

from .split_trade import SplitTrade


@runtime_checkable
class IMatchedPool[TradeKey, Context](Protocol):

    def append(
        self,
        opening: SplitTrade[TradeKey],
        closing: SplitTrade[TradeKey],
        context: Context
    ) -> None:
        ...

    def pool(
            self,
            context: Context
    ) -> Sequence[tuple[SplitTrade[TradeKey], SplitTrade[TradeKey]]]:
        ...
