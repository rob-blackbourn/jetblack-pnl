"""A basic database implementation"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlite3 import Connection

from ...core import TradingPnl, add_trade, ISecurity, IBook

from .trade import Trade
from .pools import MatchedPool, UnmatchedPool
from .tables import create_tables, drop_tables
from .pnl import save_pnl, select_pnl, ensure_pnl


def _to_decimal(number: int | Decimal) -> Decimal:
    return number if isinstance(number, Decimal) else Decimal(number)


class TradeDb:

    def __init__(self, con: Connection) -> None:
        self._con = con
        self._pnl: dict[tuple[int, int], TradingPnl] = {}

    def add_trade(
        self,
        timestamp: datetime,
        security: ISecurity[int],
        book: IBook[int],
        quantity: int | Decimal,
        price: int | Decimal,
    ) -> TradingPnl:
        cur = self._con.cursor()
        try:
            ensure_pnl(cur, security, book, timestamp)

            matched = MatchedPool(cur, security, book)
            unmatched = UnmatchedPool.Fifo(cur, security, book)
            pnl = select_pnl(cur, security, book, timestamp)

            trade = Trade.create(
                cur,
                timestamp,
                security,
                book,
                _to_decimal(quantity),
                _to_decimal(price),
            )
            pnl = add_trade(pnl, trade, security, unmatched, matched)
            save_pnl(cur, pnl, security, book, timestamp)
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
