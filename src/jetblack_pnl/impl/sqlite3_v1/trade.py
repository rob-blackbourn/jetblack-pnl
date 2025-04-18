"""A market trade"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlite3 import Cursor

from ...core import ITrade, ISecurity, IBook


class Trade(ITrade):

    def __init__(
        self,
        trade_id: int,
        timestamp: datetime,
        security: ISecurity[int],
        book: IBook[int],
        quantity: Decimal,
        price: Decimal,
    ) -> None:
        self._trade_id = trade_id
        self._timestamp = timestamp
        self._security = security
        self._book = book
        self._quantity = quantity
        self._price = price

    @property
    def trade_id(self) -> int:
        return self._trade_id

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def security(self) -> ISecurity[int]:
        return self._security

    @property
    def book(self) -> IBook[int]:
        return self._book

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    def __repr__(self) -> str:
        return f"[{self.trade_id}: {self.timestamp.isoformat()}] {self.quantity} {self.security} @ {self.price} in {self.book}"

    @classmethod
    def read(cls, cur: Cursor, trade_id: int) -> Optional[Trade]:
        cur.execute(
            """
            SELECT
                timestamp,
                security_key,
                book_key,
                quantity,
                price
            FROM
                trade
            WHERE
                trade_id = ?
            """,
            (trade_id,)
        )
        row = cur.fetchone()
        if row is None:
            return None
        (timestamp, security_key, book_key, quantity, price) = row
        return Trade(trade_id, timestamp, ticker, book, quantity, price)

    @classmethod
    def create(
        cls,
        cur: Cursor,
        timestamp: datetime,
        security: ISecurity[int],
        book: IBook[int],
        quantity: Decimal,
        price: Decimal,
    ) -> Trade:
        cur.execute(
            """
            INSERT INTO trade(timestamp, security_key, book_key, quantity, price)
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, security.key, book.key, quantity, price)
        )
        trade_id = cur.lastrowid
        assert (trade_id is not None)
        trade = Trade(
            trade_id,
            timestamp,
            security,
            book,
            quantity,
            price,
        )
        return trade
