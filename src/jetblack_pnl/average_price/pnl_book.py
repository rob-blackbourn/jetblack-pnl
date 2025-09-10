"""A P/L book"""

from decimal import Decimal

from .algorithm import add_trade

from .book import IBook
from .pnl_book_store import IPnlBookStore
from .security import ISecurity
from .trade import ITrade
from .trading_pnl import TradingPnl


class PnlBook[SecurityT: ISecurity, BookT: IBook, TradeT: ITrade]:
    """A generic implementation of a PnL book"""

    def __init__(
            self,
            store: IPnlBookStore[SecurityT, BookT, TradeT],
    ) -> None:
        self._store = store

    def get(
            self,
            security: SecurityT,
            book: BookT,
    ) -> TradingPnl:
        return self._store.get(security, book)

    def add_trade(
        self,
        security: SecurityT,
        book: BookT,
        trade: TradeT,
    ) -> TradingPnl:
        if self._store.has(security, book):
            pnl = self._store.get(security, book)
        else:
            pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

        pnl = add_trade(pnl, trade, security)
        self._store.set(security, book, trade, pnl)
        return pnl
