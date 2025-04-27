"""A P/L book"""

from decimal import Decimal
from typing import Callable

from .algorithm import add_trade

from .book import IBook
from .matched_pool import IMatchedPool
from .pnl_book_store import IPnlBookStore
from .security import ISecurity
from .trade import ITrade
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


class PnlBook[SecurityT: ISecurity, BookT: IBook, TradeT: ITrade, ContextT]:
    """A simple implementation of a PnL book"""

    def __init__(
            self,
            store: IPnlBookStore[SecurityT, BookT, TradeT, ContextT],
            matched_factory: Callable[
                [SecurityT, BookT, ContextT],
                IMatchedPool[TradeT, ContextT]
            ],
            unmatched_factory: Callable[
                [SecurityT, BookT, ContextT],
                IUnmatchedPool[TradeT, ContextT]
            ]
    ) -> None:
        self._matched_factory = matched_factory
        self._unmatched_factory = unmatched_factory
        self._store = store

    def get(
            self,
            security: SecurityT,
            book: BookT,
            context: ContextT
    ) -> tuple[TradingPnl, IUnmatchedPool[TradeT, ContextT], IMatchedPool[TradeT, ContextT]]:
        return self._store.get(security, book, context)

    def add_trade(
        self,
        security: SecurityT,
        book: BookT,
        trade: TradeT,
        context: ContextT
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
