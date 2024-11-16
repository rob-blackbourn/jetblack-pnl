"""A simple implementation for demonstrating and testing the P&L algorithm"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence, Type

from . import (
    add_trade,
    TradingPnl,
    PnlTrade,
    IMarketTrade,
    IMatchedPool,
    IUnmatchedPool
)


class MatchedPool(IMatchedPool):

    def __init__(self, pool: Sequence[tuple[PnlTrade, PnlTrade]] = ()) -> None:
        self._pool = pool

    def push(self, opening: PnlTrade, closing: PnlTrade) -> None:
        matched_trade = (opening, closing)
        self._pool = tuple((*self._pool, matched_trade))

    def __len__(self) -> int:
        return len(self._pool)

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, MatchedPool) and
            value._pool == self._pool
        )

    def __str__(self) -> str:
        return str(self._pool)


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


class MarketTrade(IMarketTrade):
    """A simple trade"""

    def __init__(self, quantity: Decimal | int, price: Decimal | int) -> None:
        self._quantity = Decimal(quantity)
        self._price = Decimal(price)

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, MarketTrade) and
            value.quantity == self.quantity and
            value.price == self.price
        )

    def __repr__(self) -> str:
        return f"{self.quantity} @ {self.price}"


def _to_decimal(number: int | Decimal) -> Decimal:
    return number if isinstance(number, Decimal) else Decimal(number)


class SimplePnl:

    def __init__(self, unmatched: Type[IUnmatchedPool] = UnmatchedPool.Fifo) -> None:
        self._unmatched = unmatched
        self._cache: dict[tuple[str, str],
                          tuple[TradingPnl, IUnmatchedPool, IMatchedPool]] = {}

    def add_trade(
        self,
        ticker: str,
        quantity: int | Decimal,
        price: int | Decimal,
        book: str
    ) -> TradingPnl:
        key = (ticker, book)
        if key in self._cache:
            pnl, unmatched, matched = self._cache[key]
        else:
            pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))
            unmatched = self._unmatched()
            matched = MatchedPool()

        trade = MarketTrade(
            _to_decimal(quantity),
            _to_decimal(price),
        )
        pnl = add_trade(pnl, trade, unmatched, matched)
        self._cache[key] = (pnl, unmatched, matched)
        return pnl
