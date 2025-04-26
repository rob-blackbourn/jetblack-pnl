"""An interface for a matched pool.
"""

from typing import Protocol, Sequence, runtime_checkable

from .split_trade import SplitTrade
from .trade import ITrade


@runtime_checkable
class IMatchedPool[TradeT: ITrade, ContextT](Protocol):

    def append(
        self,
        opening: SplitTrade[TradeT],
        closing: SplitTrade[TradeT],
        context: ContextT
    ) -> None:
        ...

    def pool(
            self,
            context: ContextT
    ) -> Sequence[tuple[SplitTrade[TradeT], SplitTrade[TradeT]]]:
        ...
