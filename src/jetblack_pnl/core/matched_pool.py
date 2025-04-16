"""An interface for a matched pool.
"""

from typing import Protocol

from .split_trade import SplitTrade
from .trade import TTradeData


class IMatchedPool(Protocol[TTradeData]):

    def append(
        self,
        opening: SplitTrade[TTradeData],
        closing: SplitTrade[TTradeData]
    ) -> None:
        ...
