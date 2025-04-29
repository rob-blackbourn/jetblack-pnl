"""Unmatched pools"""

from __future__ import annotations

from decimal import Decimal
from sqlite3 import Cursor
from typing import cast, Sequence

from ...core import SplitTrade, IUnmatchedPool

from .book import Book
from .security import Security
from .trade import Trade
from .utils import MAX_VALID_TO


class UnmatchedPool:

    class Fifo(IUnmatchedPool[Trade, Cursor]):

        def __init__(
                self,
                security: Security,
                book: Book
        ) -> None:
            self._security = security
            self._book = book

        def append(self, opening: SplitTrade[Trade], context: Cursor) -> None:
            market_trade = cast(Trade, opening.trade)

            context.execute(
                """
                INSERT INTO unmatched_trade(
                    trade_id,
                    remaining_quantity,
                    valid_from,
                    valid_to
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    market_trade.key,
                    opening.remaining_quantity,
                    market_trade.key,
                    MAX_VALID_TO
                )
            )

        def insert(self, opening: SplitTrade[Trade], context: Cursor) -> None:
            self.append(opening, context)

        def pop(self, closing: SplitTrade[Trade], context: Cursor) -> SplitTrade[Trade]:
            # Find the oldest unmatched trade that is in the valid window.
            context.execute(
                """
                SELECT
                    ut.trade_id,
                    ut.remaining_quantity,
                    ut.valid_from
                FROM
                    unmatched_trade AS ut
                JOIN
                    trade AS t
                ON
                    t.trade_id = ut.trade_id
                WHERE
                    t.security_id = ?
                AND
                    t.book_id = ?
                AND
                    ut.valid_to = ?
                ORDER BY
                    t.trade_id
                LIMIT
                    1;
                """,
                (self._security.key, self._book.key, MAX_VALID_TO)
            )
            row = context.fetchone()
            if row is None:
                raise RuntimeError("no unmatched trades")
            trade_id, remaining_quantity, valid_from = row

            # Remove from unmatched by setting the valid_to to the trade id
            # of the closing trade.
            context.execute(
                """
                update
                    unmatched_trade
                SET
                    valid_to = ?
                FROM
                    trade
                WHERE
                    trade.trade_id = unmatched_trade.trade_id
                AND
                    unmatched_trade.trade_id = ?
                AND
                    unmatched_trade.remaining_quantity = ?
                AND
                    trade.security_id = ?
                AND
                    trade.book_id = ?
                AND
                    unmatched_trade.valid_from = ?
                AND
                    unmatched_trade.valid_to = ?
                """,
                (
                    closing.trade.key,
                    trade_id,
                    remaining_quantity,
                    self._security.key,
                    self._book.key,
                    valid_from,
                    MAX_VALID_TO
                )
            )
            market_trade = Trade.load(context, trade_id)
            if market_trade is None:
                raise RuntimeError("unable to find market trade")
            pnl_trade = SplitTrade(remaining_quantity, market_trade)
            return pnl_trade

        def has(self, closing: SplitTrade[Trade], context: Cursor) -> bool:
            context.execute(
                """
                SELECT
                    COUNT(ut.trade_id) AS count
                FROM
                    unmatched_trade AS ut
                JOIN
                    trade AS t
                ON
                    t.trade_id = ut.trade_id
                AND
                    t.security_id = ?
                AND
                    t.book_id = ?
                WHERE
                    ut.valid_to > ?
                """,
                (
                    self._security.key,
                    self._book.key,
                    closing.trade.key
                )
            )
            row = context.fetchone()
            assert (row is not None)
            (count,) = row
            return count != 0

        def pool_asof(
                self,
                last_trade_id: int,
                context: Cursor
        ) -> Sequence[SplitTrade[Trade]]:
            context.execute(
                """
                SELECT
                    ut.trade_id,
                    ut.remaining_quantity
                FROM
                    unmatched_trade AS ut
                JOIN
                    trade AS t
                ON
                    t.trade_id = ut.trade_id
                WHERE
                    t.security_id = ?
                AND
                    t.book_id = ?
                AND
                    ut.valid_to > ?
                """,
                (self._security.key, self._book.key, last_trade_id)
            )

            def make_unmatched(
                    trade_id: int,
                    remaining_quantity: Decimal,
                    context: Cursor
            ) -> SplitTrade[Trade]:
                trade = Trade.load(context, trade_id)
                assert trade is not None
                return SplitTrade(remaining_quantity, trade)

            return tuple(
                make_unmatched(trade_id, remaining_quantity, context)
                for trade_id, remaining_quantity in context.fetchall()
            )

        def pool(self, context: Cursor) -> Sequence[SplitTrade[Trade]]:
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
            return self.pool_asof(row[0], context)
