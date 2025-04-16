"""An interface for a matched pool.
"""

from typing import Protocol, runtime_checkable

from .split_trade import SplitTrade
from .trade import TTradeData


@runtime_checkable
class IMatchedPool(Protocol[TTradeData]):

    def append(
        self,
        opening: SplitTrade[TTradeData],
        closing: SplitTrade[TTradeData]
    ) -> None:
        ...
