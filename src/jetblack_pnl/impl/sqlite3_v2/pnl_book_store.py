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

from .book import Book
from .matched_pool import MatchedPool
from .security import Security
from .trade import Trade
from .unmatched_pools import UnmatchedPool
from .utils import MAX_VALID_TO


class PnlBookStore(IPnlBookStore[Security, Book, Trade, Cursor]):

    def has(
            self,
            security: Security,
            book: Book,
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
        assert row is not None
        (count,) = row
        return count != 0

    def get(
            self,
            security: Security,
            book: Book,
            context: Cursor
    ) -> tuple[TradingPnl, IUnmatchedPool[Trade, Cursor], IMatchedPool[Trade, Cursor]]:
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
            security: Security,
            book: Book,
            trade: Trade,
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[Trade, Cursor],
            matched: IMatchedPool[Trade, Cursor],
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
