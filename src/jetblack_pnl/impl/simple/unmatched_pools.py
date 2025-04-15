"""A simple implementation for demonstrating and testing the P&L algorithm"""

from typing import Sequence

from ...core.types import PnlTrade, IUnmatchedPool


class UnmatchedPool:

    class Fifo(IUnmatchedPool):

        def __init__(self, pool: Sequence[PnlTrade] = ()) -> None:
            self._pool = pool

        def push(self, opening: PnlTrade) -> None:
            self._pool = tuple((*self._pool, opening))

        def pop(self, _closing: PnlTrade) -> PnlTrade:
            trade, self._pool = (self._pool[0], self._pool[1:])
            return trade

        def has(self, _closing: PnlTrade) -> bool:
            return len(self._pool) > 0

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.Fifo) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)

    class Lifo(IUnmatchedPool):

        def __init__(self, pool: Sequence[PnlTrade] = ()) -> None:
            self._pool = pool

        def push(self, opening: PnlTrade) -> None:
            self._pool = tuple((*self._pool, opening))

        def pop(self, _closing: PnlTrade) -> PnlTrade:
            trade, self._pool = (self._pool[-1], self._pool[:-1])
            return trade

        def has(self, _closing: PnlTrade) -> bool:
            return len(self._pool) > 0

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.Lifo) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)

    class BestPrice(IUnmatchedPool):

        def __init__(self, pool: Sequence[PnlTrade] = ()) -> None:
            self._pool = pool

        def push(self, opening: PnlTrade) -> None:
            self._pool = tuple((*self._pool, opening))

        def pop(self, closing: PnlTrade) -> PnlTrade:
            self._pool = sorted(self._pool, key=lambda x: x.trade.price)
            trade, self._pool = (
                (self._pool[0], self._pool[1:])
                if closing.quantity < 0
                else (self._pool[-1], self._pool[:-1])
            )
            return trade

        def has(self, _closing: PnlTrade) -> bool:
            return len(self._pool) > 0

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.BestPrice) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)

    class WorstPrice(IUnmatchedPool):

        def __init__(self, pool: Sequence[PnlTrade] = ()) -> None:
            self._pool = pool

        def push(self, opening: PnlTrade) -> None:
            self._pool = tuple((*self._pool, opening))

        def pop(self, closing: PnlTrade) -> PnlTrade:
            self._pool = sorted(self._pool, key=lambda x: x.trade.price)
            trade, self._pool = (
                (self._pool[-1], self._pool[:-1])
                if closing.quantity <= 0
                else (self._pool[0], self._pool[1:])
            )
            return trade

        def has(self, _closing: PnlTrade) -> bool:
            return len(self._pool) > 0

        def __len__(self) -> int:
            return len(self._pool)

        def __eq__(self, value: object) -> bool:
            return (
                isinstance(value, UnmatchedPool.WorstPrice) and
                value._pool == self._pool
            )

        def __str__(self) -> str:
            return str(self._pool)
