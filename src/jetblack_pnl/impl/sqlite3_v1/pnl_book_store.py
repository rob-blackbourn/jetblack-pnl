"""A basic database implementation"""

from sqlite3 import Connection

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


class PnlBookStore(IPnlBookStore[int, int, int]):

    def __init__(self, con: Connection) -> None:
        self._con = con

    def has(
            self,
            security: ISecurity[int],
            book: IBook[int]
    ) -> bool:
        cur = self._con.cursor()
        cur.execute(
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
        row = cur.fetchone()
        assert (row is not None)
        (count,) = row
        return count != 0

    def get(
            self,
            security: ISecurity[int],
            book: IBook[int]
    ) -> tuple[TradingPnl, IUnmatchedPool[int], IMatchedPool[int]]:
        cur = self._con.cursor()
        matched = MatchedPool(cur, security, book)
        unmatched = UnmatchedPool.Fifo(cur, security, book)

        cur.execute(
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
        row = cur.fetchone()
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
            unmatched: IUnmatchedPool[int],
            matched: IMatchedPool[int]
    ) -> None:
        cur = self._con.cursor()
        cur.execute(
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

        cur.execute(
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
