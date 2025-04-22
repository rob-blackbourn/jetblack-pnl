"""A basic database implementation"""

from sqlite3 import Connection

from ...core import TradingPnl, add_trade

from .matched_pool import MatchedPool
from .unmatched_pool import UnmatchedPool
from .book import Book
from .security import Security
from .trade import Trade
from .tables import create_tables, drop_tables
from .pnl import save_pnl, select_pnl, ensure_pnl


class TradeDb:

    def __init__(self, con: Connection) -> None:
        self._con = con
        self._pnl: dict[tuple[int, int], TradingPnl] = {}

    def add_trade(
        self,
        security: Security,
        book: Book,
        trade: Trade,
    ) -> TradingPnl:
        cur = self._con.cursor()
        try:
            ensure_pnl(cur, security, book, trade.key)

            matched = MatchedPool(security, book)
            unmatched = UnmatchedPool.Fifo(security, book)
            pnl = select_pnl(cur, security, book, trade.key)

            pnl = add_trade(pnl, trade, security, unmatched, matched, cur)
            save_pnl(cur, pnl, security, book, trade.key)
            self._con.commit()
            return pnl
        finally:
            cur.close()

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
