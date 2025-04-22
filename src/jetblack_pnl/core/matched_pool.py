"""An interface for a matched pool.
"""

from typing import Protocol, Sequence, runtime_checkable

from .context import TContext
from .split_trade import SplitTrade
from .trade import TTradeKey


@runtime_checkable
class IMatchedPool(Protocol[TTradeKey, TContext]):  # type: ignore

    def append(
        self,
        opening: SplitTrade[TTradeKey],
        closing: SplitTrade[TTradeKey],
        context: TContext
    ) -> None:
        ...

    def pool(
            self,
            context: TContext
    ) -> Sequence[tuple[SplitTrade[TTradeKey], SplitTrade[TTradeKey]]]:
        ...
