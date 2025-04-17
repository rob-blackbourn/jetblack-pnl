"""An interface for a matched pool.
"""

from typing import Protocol, runtime_checkable

from .split_trade import SplitTrade


@runtime_checkable
class IMatchedPool(Protocol):

    def append(
        self,
        opening: SplitTrade,
        closing: SplitTrade
    ) -> None:
        ...
