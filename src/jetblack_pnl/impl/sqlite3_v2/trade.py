"""A market trade"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Self

from sqlite3 import Cursor, Connection

from ...core import ITrade, ISecurity, IBook

from .security import Security
from .book import Book
from .utils import to_decimal


class Trade(ITrade[int]):

    def __init__(
        self,
        trade_key: int,
        timestamp: datetime,
        security: ISecurity[int],
        book: IBook[int],
        quantity: Decimal | int | str,
        price: Decimal | int | str,
    ) -> None:
        self._trade_id = trade_key
        self._timestamp = timestamp
        self._security = security
        self._book = book
        self._quantity = to_decimal(quantity)
        self._price = to_decimal(price)

    @property
    def key(self) -> int:
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
        return f"[{self.key}: {self.timestamp.isoformat()}] {self.quantity} {self.security} @ {self.price} in {self.book}"

    @classmethod
    def load(cls, cur: Cursor, key: int) -> Optional[Self]:
        cur.execute(
            """
            SELECT
                timestamp,
                security_id,
                book_id,
                quantity,
                price
            FROM
                trade
            WHERE
                trade_id = ?
            """,
            (key,)
        )
        row = cur.fetchone()
        if row is None:
            return None
        (timestamp, security_id, book_id, quantity, price) = row
        security = Security.load(cur, security_id)
        book = Book.load(cur, book_id)
        return cls(key, timestamp, security, book, quantity, price)

    @classmethod
    def create(
        cls,
        con: Connection,
        timestamp: datetime,
        security: ISecurity[int],
        book: IBook[int],
        quantity: int | str | Decimal,
        price: int | str | Decimal,
    ) -> Self:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO trade(timestamp, security_id, book_id, quantity, price)
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, security.key, book.key, quantity, price)
        )
        trade_id = cur.lastrowid
        assert trade_id is not None
        trade = cls(
            trade_id,
            timestamp,
            security,
            book,
            to_decimal(quantity),
            to_decimal(price),
        )
        return trade
