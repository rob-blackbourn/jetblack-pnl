"""Matched pools"""

from decimal import Decimal
from sqlite3 import Cursor
from typing import Sequence

from ...core import IMatchedPool

from .book import Book
from .security import Security
from .trade import Trade
from .utils import MAX_VALID_TO


class MatchedPool(IMatchedPool[Trade, Cursor]):

    def __init__(
            self,
            security: Security,
            book: Book
    ) -> None:
        self._security = security
        self._book = book

    def append(
            self,
            closing_quantity: Decimal,
            opening_trade: Trade,
            closing_trade: Trade,
            context: Cursor
    ) -> None:
        # Insert the new match.
        context.execute(
            """
            INSERT INTO matched_trade(
                closing_quantity,
                opening_trade_id,
                closing_trade_id,
                valid_from,
                valid_to
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                closing_quantity,
                opening_trade.key,
                closing_trade.key,
                closing_trade.key,
                MAX_VALID_TO
            )
        )

    def pool_asof(
            self,
            last_trade_id: int,
            context: Cursor
    ) -> Sequence[tuple[Decimal, Trade, Trade]]:
        context.execute(
            """
            SELECT
                mt.closing_quantity,
                mt.opening_trade_id,
                mt.closing_trade_id
            FROM
                matched_trade AS mt
            JOIN
                trade AS ct
            ON
                ct.trade_id = mt.closing_trade_id
            WHERE
                ct.security_id = ?
            AND
                ct.book_id = ?
            AND
                mt.valid_to > ?
            """,
            (self._security.key, self._book.key, last_trade_id)
        )

        def make_match(
                quantity: Decimal,
                opening_trade_id: int,
                closing_trade_id: int,
                context: Cursor
        ) -> tuple[Decimal, Trade, Trade]:
            opening_trade = Trade.load(context, opening_trade_id)
            assert opening_trade is not None
            closing_trade = Trade.load(context, closing_trade_id)
            assert closing_trade is not None
            return (
                quantity,
                opening_trade,
                closing_trade
            )

        return tuple(
            make_match(quantity, opening_trade_id, closing_trade_id, context)
            for quantity, opening_trade_id, closing_trade_id in context.fetchall()
        )

    def pool(self, context: Cursor) -> Sequence[tuple[Decimal, Trade, Trade]]:
        context.execute(
            """
            SELECT
                MAX(trade_id) AS last_trade_id
            FROM
                trade
            WHERE
                security_id = ?
            AND
                book_id = ?
            """,
            (self._security.key, self._book.key)
        )
        row = context.fetchone()
        if row is None:
            return ()
        last_trade_id = row[0]
        return self.pool_asof(last_trade_id, context)
