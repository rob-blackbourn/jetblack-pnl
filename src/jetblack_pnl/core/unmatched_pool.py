"""An interface for an unmatched pool.
"""

from typing import Protocol, Sequence, runtime_checkable

from .split_trade import SplitTrade
from .trade import ITrade


@runtime_checkable
class IUnmatchedPool[Trade: ITrade, Context](Protocol):  # type: ignore
    """A pool of unmatched trades"""

    def append(
            self,
            opening: SplitTrade[Trade],
            context: Context
    ) -> None:
        ...

    def insert(
            self,
            opening: SplitTrade[Trade],
            context: Context
    ) -> None:
        ...

    def pop(
            self,
            closing: SplitTrade[Trade],
            context: Context
    ) -> SplitTrade[Trade]:
        ...

    def has(
            self,
            closing: SplitTrade[Trade],
            context: Context
    ) -> bool:
        ...

    def pool(self, context: Context) -> Sequence[SplitTrade[Trade]]:
        ...
