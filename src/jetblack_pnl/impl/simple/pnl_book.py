"""A simple implementation of a PnL book"""

from decimal import Decimal
from typing import Callable, Generic

from ...core.algorithm import add_trade

from ...core.types import (
    TBookKey,
    IBook,
    TSecurityKey,
    ISecurity,
    TradingPnl,
    IMatchedPool,
    IUnmatchedPool
)


from .trade import Trade


class PnlBook(Generic[TSecurityKey, TBookKey]):
    """A simple implementation of a PnL book"""

    def __init__(
            self,
            matched_factory: Callable[[], IMatchedPool],
            unmatched_factory: Callable[[], IUnmatchedPool]
    ) -> None:
        self._matched_factory = matched_factory
        self._unmatched_factory = unmatched_factory
        self._cache: dict[
            tuple[TSecurityKey, TBookKey],
            tuple[TradingPnl, IUnmatchedPool, IMatchedPool]
        ] = {}

    def add_trade(
        self,
        security: ISecurity[TSecurityKey],
        book: IBook[TBookKey],
        quantity: int | Decimal | str,
        price: int | Decimal | str,
    ) -> TradingPnl:
        key = (security.key, book.key)
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
