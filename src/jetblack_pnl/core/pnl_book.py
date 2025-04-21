"""A P/L book"""

from decimal import Decimal
from typing import Callable, Generic

from .algorithm import add_trade

from .book import IBook, TBookKey
from .context import TContext
from .matched_pool import IMatchedPool
from .pnl_book_store import IPnlBookStore
from .security import ISecurity, TSecurityKey
from .trade import TTradeKey, ITrade
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


class PnlBook(Generic[TSecurityKey, TBookKey, TTradeKey, TContext]):
    """A simple implementation of a PnL book"""

    def __init__(
            self,
            store: IPnlBookStore[TSecurityKey, TBookKey, TTradeKey, TContext],
            matched_factory: Callable[
                [ISecurity[TSecurityKey], IBook[TBookKey], TContext],
                IMatchedPool[TTradeKey, TContext]
            ],
            unmatched_factory: Callable[
                [ISecurity[TSecurityKey], IBook[TBookKey], TContext],
                IUnmatchedPool[TTradeKey, TContext]
            ]
    ) -> None:
        self._matched_factory = matched_factory
        self._unmatched_factory = unmatched_factory
        self._store = store

    def add_trade(
        self,
        security: ISecurity[TSecurityKey],
        book: IBook[TBookKey],
        trade: ITrade[TTradeKey],
        context: TContext
    ) -> TradingPnl:
        if self._store.has(security, book, context):
            pnl, unmatched, matched = self._store.get(security, book, context)
        else:
            pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))
            unmatched = self._unmatched_factory(security, book, context)
            matched = self._matched_factory(security, book, context)

        pnl = add_trade(pnl, trade, security, unmatched, matched, context)
        self._store.set(security, book, trade, pnl,
                        unmatched, matched, context)
        return pnl
