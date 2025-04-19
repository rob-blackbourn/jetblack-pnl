"""Matched and unmatched pools"""

from datetime import datetime
from sqlite3 import Cursor
from typing import cast, Sequence

from ...core import (
    SplitTrade,
    IMatchedPool,
    ISecurity,
    IBook
)

from .trade import Trade
from .pnl import MAX_VALID_TO


class MatchedPool(IMatchedPool[int]):

    def __init__(
            self,
            cur: Cursor,
            security: ISecurity[int],
            book: IBook[int]
    ) -> None:
        self._cur = cur
        self._security = security
        self._book = book

    def append(
            self,
            opening: SplitTrade[int],
            closing: SplitTrade[int]
    ) -> None:
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
                opening.trade.key,
                closing.trade.key,
                cast(Trade, closing.trade).timestamp,
                MAX_VALID_TO
            )
        )

    def pool_asof(
            self,
            asof: datetime
    ) -> Sequence[tuple[SplitTrade[int], SplitTrade[int]]]:
        self._cur.execute(
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
            (self._security.key, self._book.key, asof, asof)
        )

        def make_match(
                opening_trade_id: int,
                closing_trade_id: int
        ) -> tuple[SplitTrade[int], SplitTrade[int]]:
            opening_trade = Trade.load(self._cur, opening_trade_id)
            assert opening_trade is not None
            closing_trade = Trade.load(self._cur, closing_trade_id)
            assert closing_trade is not None
            return (
                SplitTrade(opening_trade.quantity, opening_trade),
                SplitTrade(closing_trade.quantity, closing_trade)
            )

        return tuple(
            make_match(opening_trade_id, closing_trade_id)
            for opening_trade_id, closing_trade_id in self._cur.fetchall()
        )

    @property
    def pool(self) -> Sequence[tuple[SplitTrade[int], SplitTrade[int]]]:
        return self.pool_asof(datetime.now())
