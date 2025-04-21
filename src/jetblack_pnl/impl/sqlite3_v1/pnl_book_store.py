"""A basic database implementation"""

from sqlite3 import Cursor

from ...core import (
    IPnlBookStore,
    TradingPnl,
    IUnmatchedPool,
    IMatchedPool,
    ISecurity,
    IBook,
    ITrade
)

from .matched_pool import MatchedPool
from .unmatched_pool import UnmatchedPool
from .pnl import MAX_VALID_TO


class PnlBookStore(IPnlBookStore[int, int, int, Cursor]):

    def has(
            self,
            security: ISecurity[int],
            book: IBook[int],
            context: Cursor,
    ) -> bool:
        context.execute(
            """
            SELECT
                COUNT(*) AS count
            FROM
                pnl
            WHERE
                security_id = ?
            AND
                book_id = ?
            AND
                valid_to = ?;
            """,
            (security.key, book.key, MAX_VALID_TO)
        )
        row = context.fetchone()
        assert (row is not None)
        (count,) = row
        return count != 0

    def get(
            self,
            security: ISecurity[int],
            book: IBook[int],
            context: Cursor
    ) -> tuple[TradingPnl, IUnmatchedPool[int, Cursor], IMatchedPool[int, Cursor]]:
        matched = MatchedPool(security, book)
        unmatched = UnmatchedPool.Fifo(security, book)

        context.execute(
            """
            SELECT
                quantity,
                cost,
                realized
            FROM
                pnl
            WHERE
                security_id = ?
            AND
                book_id = ?
            AND
                valid_to = ?
            """,
            (security.key, book.key, MAX_VALID_TO)
        )
        row = context.fetchone()
        if row is None:
            raise KeyError()
        (quantity, cost, realized) = row
        pnl = TradingPnl(quantity, cost, realized)

        return (pnl, unmatched, matched)

    def set(
            self,
            security: ISecurity[int],
            book: IBook[int],
            trade: ITrade[int],
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[int, Cursor],
            matched: IMatchedPool[int, Cursor],
            context: Cursor
    ) -> None:
        context.execute(
            """
            UPDATE
                pnl
            SET
                valid_to = ?
            WHERE
                security_id = ?
            AND
                book_id = ?
            AND
                valid_from <= ?
            AND
                valid_to = ?;
            """,
            (trade.key, security.key, book.key, trade.key, MAX_VALID_TO)
        )

        context.execute(
            """
            INSERT INTO pnl
            (
                security_id,
                book_id,
                quantity,
                cost,
                realized,
                valid_from,
                valid_to
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            );
            """,
            (
                security.key,
                book.key,
                pnl.quantity,
                pnl.cost,
                pnl.realized,
                trade.key,
                MAX_VALID_TO
            )
        )
