"""A simple implementation of a PnL book"""

from decimal import Decimal
from typing import Callable, Generic

from .algorithm import add_trade

from .book import IBook, TBookKey
from .matched_pool import IMatchedPool
from .security import ISecurity, TSecurityKey
from .trade import TTradeKey, ITrade
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


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
        trade: ITrade[TTradeKey],
    ) -> TradingPnl:
        key = (security.key, book.key)
        if key in self._cache:
            pnl, unmatched, matched = self._cache[key]
        else:
            pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))
            unmatched = self._unmatched_factory()
            matched = self._matched_factory()

        pnl = add_trade(pnl, trade, security, unmatched, matched)
        self._cache[key] = (pnl, unmatched, matched)
        return pnl
