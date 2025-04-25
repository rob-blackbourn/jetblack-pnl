"""A basic database implementation"""

from sqlite3 import Connection, Cursor

from ...core import TradingPnl, PnlBook

from .book import Book
from .matched_pool import MatchedPool
from .security import Security
from .trade import Trade
from .unmatched_pools import UnmatchedPool
from .tables import create_tables, drop_tables
from .pnl_book_store import PnlBookStore


class DbPnlBook(PnlBook[Security, Book, Trade, Cursor]):

    def __init__(self, con: Connection) -> None:
        self._con = con
        super().__init__(
            PnlBookStore(),
            lambda security, book, context: MatchedPool(security, book),
            lambda security, book, context: UnmatchedPool.Fifo(security, book),
        )
        self._pnl: dict[tuple[int, int], TradingPnl] = {}

    def add(
        self,
        trade: Trade,
    ) -> TradingPnl:
        cur = self._con.cursor()
        pnl = super().add_trade(trade.security, trade.book, trade, cur)
        self._con.commit()
        cur.close()
        return pnl

    def create_tables(self) -> None:
        cur = self._con.cursor()
        try:
            create_tables(cur)
        finally:
            cur.close()

    def drop(self) -> None:
        cur = self._con.cursor()
        try:
            drop_tables(cur)
        finally:
            cur.close()
