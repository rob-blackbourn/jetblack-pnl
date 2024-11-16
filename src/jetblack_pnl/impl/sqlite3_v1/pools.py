"""Matched and unmatched pools"""

from __future__ import annotations

from sqlite3 import Cursor
from typing import cast

from ...core import (
    PnlTrade,
    IMatchedPool,
    IUnmatchedPool,
)

from .market_trade import MarketTrade
from .pnl import MAX_VALID_TO


class MatchedPool(IMatchedPool):

    def __init__(self, cur: Cursor, ticker: str, book: str) -> None:
        self._cur = cur
        self._ticker = ticker
        self._book = book

    def push(self, opening: PnlTrade, closing: PnlTrade) -> None:
        self._cur.execute(
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
                cast(MarketTrade, opening.trade).trade_id,
                cast(MarketTrade, closing.trade).trade_id,
                cast(MarketTrade, closing.trade).timestamp,
                MAX_VALID_TO
            )
        )


class UnmatchedPool:

    class Fifo(IUnmatchedPool):

        def __init__(self, cur: Cursor, ticker: str, book: str) -> None:
            self._cur = cur
            self._ticker = ticker
            self._book = book

        def push(self, opening: PnlTrade) -> None:
            market_trade = cast(MarketTrade, opening.trade)

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
                    market_trade.trade_id,
                    opening.quantity,
                    market_trade.timestamp,
                    MAX_VALID_TO
                )
            )

        def pop(self, closing: PnlTrade) -> PnlTrade:
            # Find the oldest unmatched trade that is in the valid window.
            timestamp = cast(MarketTrade, closing.trade).timestamp
            self._cur.execute(
                """
                SELECT
                    t.timestamp,
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
                (timestamp, MAX_VALID_TO)
            )
            row = self._cur.fetchone()
            if row is None:
                raise RuntimeError("no unmatched trades")
            timestamp, trade_id, quantity, valid_from = row

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
                    timestamp,
                    trade_id,
                    quantity,
                    valid_from,
                    MAX_VALID_TO
                )
            )
            market_trade = MarketTrade.read(self._cur, trade_id)
            if market_trade is None:
                raise RuntimeError("unable to find market trade")
            pnl_trade = PnlTrade(quantity, market_trade)
            return pnl_trade

        def has(self, closing: PnlTrade) -> bool:
            timestamp = cast(MarketTrade, closing.trade).timestamp
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
                    t.ticker = ?
                AND
                    t.book = ?
                WHERE
                    ut.valid_from <= ? AND ? < ut.valid_to
                """,
                (
                    self._ticker,
                    self._book,
                    timestamp,
                    timestamp
                )
            )
            row = self._cur.fetchone()
            assert (row is not None)
            (count,) = row
            return count != 0
