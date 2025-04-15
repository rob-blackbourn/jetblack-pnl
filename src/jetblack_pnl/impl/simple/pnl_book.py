"""A simple implementation of a PnL book"""

from decimal import Decimal
from typing import Type

from ...core.algorithm import add_trade

from ...core.types import (
    TradingPnl,
    IMatchedPool,
    IUnmatchedPool
)


from .unmatched_pools import UnmatchedPool
from .matched_pool import MatchedPool
from .trade import Trade


class PnlBook:

    def __init__(
            self,
            unmatched: Type[IUnmatchedPool] = UnmatchedPool.Fifo
    ) -> None:
        self._unmatched = unmatched
        self._cache: dict[
            tuple[str, str],
            tuple[TradingPnl, IUnmatchedPool, IMatchedPool]
        ] = {}

    def add_trade(
        self,
        ticker: str,
        book: str,
        quantity: int | Decimal | str,
        price: int | Decimal | str,
    ) -> TradingPnl:
        key = (ticker, book)
        if key in self._cache:
            pnl, unmatched, matched = self._cache[key]
        else:
            pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))
            unmatched = self._unmatched()
            matched = MatchedPool()

        trade = Trade(quantity, price)
        pnl = add_trade(pnl, trade, unmatched, matched)
        self._cache[key] = (pnl, unmatched, matched)
        return pnl
