"""SQL statements"""

from datetime import datetime
from decimal import Decimal

from sqlite3 import Cursor

from ...core import TradingPnl, ISecurity, IBook

MAX_VALID_TO = datetime(9999, 12, 31, 23, 59, 59)


def ensure_pnl(
        cur: Cursor,
        security: ISecurity[int],
        book: IBook[int],
        timestamp: datetime
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
        (security.key, book.key, timestamp)
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
        timestamp: datetime
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
        (security.key, book.key, timestamp, MAX_VALID_TO)
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
        timestamp: datetime
) -> None:
    cur.execute(
        """
        UPDATE
            pnl
        SET
            valid_to = ?
        WHERE
            ticker = ?
        AND
            book = ?
        AND
            valid_from <= ?
        AND
            valid_to = ?;
        """,
        (timestamp, security.key, book.key, timestamp, MAX_VALID_TO)
    )

    cur.execute(
        """
        INSERT INTO pnl
        (
            ticker,
            book,
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
            timestamp,
            MAX_VALID_TO
        )
    )
