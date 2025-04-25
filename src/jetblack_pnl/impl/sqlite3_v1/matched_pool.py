"""Matched and unmatched pools"""

from sqlite3 import Cursor
from typing import Sequence

from ...core import SplitTrade, IMatchedPool

from .book import Book
from .security import Security
from .trade import Trade
from .pnl import MAX_VALID_TO


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
            opening: SplitTrade[Trade],
            closing: SplitTrade[Trade],
            context: Cursor
    ) -> None:
        context.execute(
            """
            INSERT INTO matched_trade(
                opening_trade_id,
                closing_trade_id,
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
                opening.trade.key,
                closing.trade.key,
                closing.trade.key,
                MAX_VALID_TO
            )
        )

    def pool_asof(
            self,
            last_trade_id: int,
            context: Cursor
    ) -> Sequence[tuple[SplitTrade[Trade], SplitTrade[Trade]]]:
        context.execute(
            """
            SELECT
                mt.opening_trade_id,
                mt.closing_trade_id
            FROM
                matched_trade AS mt
            JOIN
                trade AS ot
            ON
                ot.trade_id = mt.opening_trade_id
            JOIN
                trade AS ct
            ON
                ct.trade_id = mt.closing_trade_id
            JOIN
                security AS os
            ON
                os.security_id = ot.security_id
            JOIN
                security AS cs
            ON
                cs.security_id = ct.security_id
            JOIN
                book AS ob
            ON
                ob.book_id = ot.book_id
            JOIN
                book AS cb
            ON
                cb.book_id = ct.book_id
            WHERE
                ot.security_id = ?
            AND
                ct.book_id = ?
            AND
                valid_from <= ?
            AND
                valid_to = ?
            """,
            (self._security.key, self._book.key, last_trade_id, last_trade_id)
        )

        def make_match(
                opening_trade_id: int,
                closing_trade_id: int,
                context: Cursor
        ) -> tuple[SplitTrade[Trade], SplitTrade[Trade]]:
            opening_trade = Trade.load(context, opening_trade_id)
            assert opening_trade is not None
            closing_trade = Trade.load(context, closing_trade_id)
            assert closing_trade is not None
            return (
                SplitTrade(opening_trade.quantity, opening_trade),
                SplitTrade(closing_trade.quantity, closing_trade)
            )

        return tuple(
            make_match(opening_trade_id, closing_trade_id, context)
            for opening_trade_id, closing_trade_id in context.fetchall()
        )

    def pool(self, context: Cursor) -> Sequence[tuple[SplitTrade[Trade], SplitTrade[Trade]]]:
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
        last_trade_id = context.fetchone()
        if last_trade_id is None:
            return ()
        return self.pool_asof(last_trade_id, context)
