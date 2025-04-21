"""An interface for a matched pool.
"""

from typing import Protocol, runtime_checkable

from .split_trade import SplitTrade
from .trade import TTradeKey


@runtime_checkable
class IMatchedPool(Protocol[TTradeKey]):  # type: ignore

    def append(
        self,
        opening: SplitTrade[TTradeKey],
        closing: SplitTrade[TTradeKey]
    ) -> None:
        ...
