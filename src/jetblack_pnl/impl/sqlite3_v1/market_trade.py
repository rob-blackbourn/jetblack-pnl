"""A market trade"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlite3 import Cursor

from ...core import IMarketTrade


class MarketTrade(IMarketTrade):

    def __init__(
        self,
        trade_id: int,
        timestamp: datetime,
        ticker: str,
        quantity: Decimal,
        price: Decimal,
        book: str
    ) -> None:
        self._trade_id = trade_id
        self._timestamp = timestamp
        self._ticker = ticker
        self._quantity = quantity
        self._price = price
        self._book = book

    @property
    def trade_id(self) -> int:
        return self._trade_id

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def ticker(self) -> str:
        return self._ticker

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    @property
    def book(self) -> str:
        return self._book

    def __repr__(self) -> str:
        return f"[{self.trade_id}: {self.timestamp.isoformat()}] {self.quantity} {self.ticker} @ {self.price} in {self.book}"

    @classmethod
    def read(cls, cur: Cursor, trade_id: int) -> Optional[MarketTrade]:
        cur.execute(
            """
            SELECT
                timestamp,
                ticker,
                quantity,
                price,
                book
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
        (timestamp, ticker, quantity, price, book) = row
        return MarketTrade(trade_id, timestamp, ticker, quantity, price, book)

    @classmethod
    def create(
        cls,
        cur: Cursor,
        timestamp: datetime,
        ticker: str,
        quantity: Decimal,
        price: Decimal,
        book: str
    ) -> MarketTrade:
        cur.execute(
            """
            INSERT INTO trade(timestamp, ticker, quantity, price, book)
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, ticker, quantity, price, book)
        )
        trade_id = cur.lastrowid
        assert (trade_id is not None)
        trade = MarketTrade(
            trade_id,
            timestamp,
            ticker,
            quantity,
            price,
            book
        )
        return trade
