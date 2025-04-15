"""A simple implementation of a PnL book"""

from decimal import Decimal
from typing import Type

from ...core.algorithm import add_trade

from ...core.types import (
    TradingPnl,
    IMatchedPool,
    IUnmatchedPool
)


from .trade import Trade


class PnlBook:

    def __init__(
            self,
            matched_factory: Type[IMatchedPool],
            unmatched_factory: Type[IUnmatchedPool]
    ) -> None:
        self._matched_factory = matched_factory
        self._unmatched_factory = unmatched_factory
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
            unmatched = self._unmatched_factory()
            matched = self._matched_factory()

        trade = Trade(quantity, price)
        pnl = add_trade(pnl, trade, unmatched, matched)
        self._cache[key] = (pnl, unmatched, matched)
        return pnl
