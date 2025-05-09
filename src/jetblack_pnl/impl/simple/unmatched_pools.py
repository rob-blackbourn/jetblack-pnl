"""A simple implementation of unmatched pools"""

from typing import Sequence

from ...core import SplitTrade, IUnmatchedPool

from .trade import Trade
from .types import Context


class UnmatchedPool:

    class Fifo(IUnmatchedPool[Trade, Context]):

        def __init__(self, pool: Sequence[SplitTrade[Trade]] = ()) -> None:
            self._pool = pool

        def append(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((*self._pool, opening))

        def insert(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((opening, *self._pool))

        def pop(self, _closing: SplitTrade[Trade], context: Context) -> SplitTrade[Trade]:
            trade, self._pool = (self._pool[0], self._pool[1:])
            return trade

        def has(self, _closing: SplitTrade[Trade], context: Context) -> bool:
            return len(self._pool) > 0

        def pool(self, context: Context) -> Sequence[SplitTrade[Trade]]:
            """Returns the unmatched pool"""
            return self._pool

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.Fifo) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)

        def __repr__(self) -> str:
            return str(self._pool)

    class Lifo(IUnmatchedPool[Trade, Context]):

        def __init__(self, pool: Sequence[SplitTrade[Trade]] = ()) -> None:
            self._pool = pool

        def append(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((*self._pool, opening))

        def insert(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((opening, *self._pool))

        def pop(
                self,
                _closing: SplitTrade[Trade],
                context: Context
        ) -> SplitTrade[Trade]:
            trade, self._pool = (self._pool[-1], self._pool[:-1])
            return trade

        def has(self, _closing: SplitTrade[Trade], context: Context) -> bool:
            return len(self._pool) > 0

        def pool(self, context: Context) -> Sequence[SplitTrade[Trade]]:
            """Returns the unmatched pool"""
            return self._pool

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.Lifo) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)

        def __repr__(self) -> str:
            return str(self._pool)

    class BestPrice(IUnmatchedPool[Trade, Context]):

        def __init__(self, pool: Sequence[SplitTrade[Trade]] = ()) -> None:
            self._pool = pool

        def append(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((*self._pool, opening))

        def insert(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((opening, *self._pool))

        def pop(self, closing: SplitTrade[Trade], context: Context) -> SplitTrade[Trade]:
            self._pool = sorted(self._pool, key=lambda x: x.trade.price)
            trade, self._pool = (
                (self._pool[0], self._pool[1:])
                if closing.remaining_quantity < 0
                else (self._pool[-1], self._pool[:-1])
            )
            return trade

        def has(self, _closing: SplitTrade[Trade], context: Context) -> bool:
            return len(self._pool) > 0

        def pool(self, context: Context) -> Sequence[SplitTrade[Trade]]:
            """Returns the unmatched pool"""
            return self._pool

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.BestPrice) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)

        def __repr__(self) -> str:
            return str(self._pool)

    class WorstPrice(IUnmatchedPool[Trade, Context]):

        def __init__(self, pool: Sequence[SplitTrade[Trade]] = ()) -> None:
            self._pool = pool

        def append(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((*self._pool, opening))

        def insert(self, opening: SplitTrade[Trade], context: Context) -> None:
            self._pool = tuple((opening, *self._pool))

        def pop(self, closing: SplitTrade[Trade], context: Context) -> SplitTrade[Trade]:
            self._pool = sorted(self._pool, key=lambda x: x.trade.price)
            trade, self._pool = (
                (self._pool[-1], self._pool[:-1])
                if closing.remaining_quantity <= 0
                else (self._pool[0], self._pool[1:])
            )
            return trade

        def has(self, _closing: SplitTrade[Trade], context: Context) -> bool:
            return len(self._pool) > 0

        def pool(self, context: Context) -> Sequence[SplitTrade[Trade]]:
            """Returns the unmatched pool"""
            return self._pool

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.WorstPrice) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)

        def __repr__(self) -> str:
            return str(self._pool)
