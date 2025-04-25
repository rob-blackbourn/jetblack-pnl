"""An interface for a matched pool.
"""

from typing import Protocol, Sequence, runtime_checkable

from .split_trade import SplitTrade
from .trade import ITrade


@runtime_checkable
class IMatchedPool[Trade: ITrade, Context](Protocol):

    def append(
        self,
        opening: SplitTrade[Trade],
        closing: SplitTrade[Trade],
        context: Context
    ) -> None:
        ...

    def pool(
            self,
            context: Context
    ) -> Sequence[tuple[SplitTrade[Trade], SplitTrade[Trade]]]:
        ...
