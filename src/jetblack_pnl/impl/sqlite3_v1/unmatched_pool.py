"""Matched and unmatched pools"""

from __future__ import annotations

from decimal import Decimal
from sqlite3 import Cursor
from typing import cast, Sequence

from ...core import (
    SplitTrade,
    IUnmatchedPool,
    ISecurity,
    IBook
)

from .trade import Trade
from .pnl import MAX_VALID_TO


class UnmatchedPool:

    class Fifo(IUnmatchedPool[int]):

        def __init__(
                self,
                cur: Cursor,
                security: ISecurity[int],
                book: IBook[int]
        ) -> None:
            self._cur = cur
            self._security = security
            self._book = book

        def append(self, opening: SplitTrade[int]) -> None:
            market_trade = cast(Trade, opening.trade)

            self._cur.execute(
                """
                INSERT INTO unmatched_trade(
                    trade_id,
                    quantity,
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
                    opening.quantity,
                    market_trade.key,
                    MAX_VALID_TO
                )
            )

        def insert(self, opening: SplitTrade[int]) -> None:
            self.append(opening)

        def pop(self, closing: SplitTrade[int]) -> SplitTrade[int]:
            # Find the oldest unmatched trade that is in the valid window.
            self._cur.execute(
                """
                SELECT
                    t.trade_id,
                    ut.quantity,
                    ut.valid_from
                FROM
                    unmatched_trade AS ut
                JOIN
                    trade AS t
                ON
                    t.trade_id = ut.trade_id
                WHERE
                    ut.valid_from <= ?
                AND
                    ut.valid_to = ?
                ORDER BY
                    t.timestamp,
                    t.trade_id
                LIMIT
                    1;
                """,
                (closing.trade.key, MAX_VALID_TO)
            )
            row = self._cur.fetchone()
            if row is None:
                raise RuntimeError("no unmatched trades")
            trade_id, quantity, valid_from = row

            # Remove from unmatched by setting the valid_to to the trade's
            # timestamp
            self._cur.execute(
                """
                update
                    unmatched_trade
                SET
                    valid_to = ?
                WHERE
                    trade_id = ?
                AND
                    quantity = ?
                AND
                    valid_from = ?
                AND
                    valid_to = ?
                """,
                (
                    closing.trade.key,
                    trade_id,
                    quantity,
                    valid_from,
                    MAX_VALID_TO
                )
            )
            market_trade = Trade.load(self._cur, trade_id)
            if market_trade is None:
                raise RuntimeError("unable to find market trade")
            pnl_trade = SplitTrade(quantity, market_trade)
            return pnl_trade

        def has(self, closing: SplitTrade[int]) -> bool:
            self._cur.execute(
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
                    ut.valid_from <= ? AND ? < ut.valid_to
                """,
                (
                    self._security.key,
                    self._book.key,
                    closing.trade.key,
                    closing.trade.key
                )
            )
            row = self._cur.fetchone()
            assert (row is not None)
            (count,) = row
            return count != 0

        def pool_asof(
                self,
                last_trade_id: int
        ) -> Sequence[SplitTrade[int]]:
            self._cur.execute(
                """
                SELECT
                    trade_id,
                    quantity
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
                    ut.valid_from <= ? AND ? < ut.valid_to
                """,
                (self._security.key, self._book.key, last_trade_id, MAX_VALID_TO)
            )

            def make_unmatched(
                    trade_id: int,
                    quantity: Decimal
            ) -> SplitTrade[int]:
                trade = Trade.load(self._cur, trade_id)
                assert trade is not None
                return SplitTrade(quantity, trade)

            return tuple(
                make_unmatched(trade_id, quantity)
                for trade_id, quantity in self._cur.fetchall()
            )

        @property
        def pool(self) -> Sequence[SplitTrade[int]]:
            self._cur.execute(
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
            last_trade_id = self._cur.fetchone()
            if last_trade_id is None:
                return ()
            return self.pool_asof(last_trade_id)
