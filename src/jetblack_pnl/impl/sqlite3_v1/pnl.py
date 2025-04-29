"""SQL statements"""

from decimal import Decimal
from sqlite3 import Cursor
from typing import Sequence

from ...core import TradingPnl, ISecurity, IBook

from .utils import MAX_VALID_TO


def has_pnl(
        cur: Cursor,
        security: ISecurity[int],
        book: IBook[int]
) -> bool:
    # There should be no pnl on or after this timestamp.
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


def ensure_pnl(
        cur: Cursor,
        security: ISecurity[int],
        book: IBook[int],
        last_trade_id: int
) -> None:
    # There should be no pnl on or after this timestamp.
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
            valid_from >= ?;
        """,
        (security.key, book.key, last_trade_id)
    )
    row = cur.fetchone()
    assert (row is not None)
    (count,) = row
    if count != 0:
        raise RuntimeError("there is already p/l for this timestamp")


def select_pnl(
        cur: Cursor,
        security: ISecurity[int],
        book: IBook[int],
        last_trade_id: int
) -> TradingPnl:
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
            valid_from <= ?
        AND
            valid_to = ?
        """,
        (security.key, book.key, last_trade_id, MAX_VALID_TO)
    )
    row = cur.fetchone()
    if row is None:
        return TradingPnl(Decimal(0), Decimal(0), Decimal(0))
    (quantity, cost, realized) = row

    return TradingPnl(quantity, cost, realized)


def save_pnl(
        cur: Cursor,
        pnl: TradingPnl,
        security: ISecurity[int],
        book: IBook[int],
        last_trade_id: int
) -> None:
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
        (last_trade_id, security.key, book.key, last_trade_id, MAX_VALID_TO)
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
            last_trade_id,
            MAX_VALID_TO
        )
    )


def pnl_report(
        cur: Cursor,
        last_trade_id: int
) -> Sequence[tuple[str, str, TradingPnl]]:
    cur.execute(
        """
        SELECT
            s.name AS security,
            b.name AS book.
            p.quantity,
            p.cost,
            p.realized
        FROM
            pnl AS p
        JOIN
            security AS s
        ON
            s.security_id = p.security_id
        JOIN
            book as b
        ON
            b.book_id = p.book_id
        WHERE
            valid_from <= ?
        AND
            valid_to = ?
        """,
        (last_trade_id, MAX_VALID_TO)
    )
    return [
        (security,  book, TradingPnl(quantity, cost, realized))
        for security, book, quantity, cost, realized in cur.fetchall()
    ]
