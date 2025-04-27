"""An interface for a matched pool.
"""

from decimal import Decimal
from typing import Protocol, Sequence, runtime_checkable

from .trade import ITrade


@runtime_checkable
class IMatchedPool[TradeT: ITrade, ContextT](Protocol):

    def append(
        self,
        closing_quantity: Decimal,
        opening_trade: TradeT,
        closing_trade: TradeT,
        context: ContextT
    ) -> None:
        ...

    def pool(
            self,
            context: ContextT
    ) -> Sequence[tuple[Decimal, TradeT, TradeT]]:
        ...
