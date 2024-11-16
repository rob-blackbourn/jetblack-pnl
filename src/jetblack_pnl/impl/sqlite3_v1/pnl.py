"""SQL statements"""

from datetime import datetime
from decimal import Decimal

from sqlite3 import Cursor

from ...core import TradingPnl

MAX_VALID_TO = datetime(9999, 12, 31, 23, 59, 59)


def ensure_pnl(cur: Cursor, ticker: str, book: str, timestamp: datetime) -> None:
    # There should be no pnl on or after this timestamp.
    cur.execute(
        """
        SELECT
            COUNT(*) AS count
        FROM
            pnl
        WHERE
            ticker = ?
        AND
            book = ?
        AND
            valid_from >= ?;
        """,
        (ticker, book, timestamp)
    )
    row = cur.fetchone()
    assert (row is not None)
    (count,) = row
    if count != 0:
        raise RuntimeError("there is already p/l for this timestamp")


def select_pnl(cur: Cursor, ticker: str, book: str, timestamp: datetime) -> TradingPnl:
    cur.execute(
        """
        SELECT
            quantity,
            cost,
            realized
        FROM
            pnl
        WHERE
            ticker = ?
        AND
            book = ?
        AND
            valid_from <= ?
        AND
            valid_to = ?
        """,
        (ticker, book, timestamp, MAX_VALID_TO)
    )
    row = cur.fetchone()
    if row is None:
        return TradingPnl(Decimal(0), Decimal(0), Decimal(0))
    (quantity, cost, realized) = row

    return TradingPnl(quantity, cost, realized)


def save_pnl(cur: Cursor, pnl: TradingPnl, ticker: str, book: str, timestamp: datetime) -> None:
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
        (timestamp, ticker, book, timestamp, MAX_VALID_TO)
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
            ticker,
            book,
            pnl.quantity,
            pnl.cost,
            pnl.realized,
            timestamp,
            MAX_VALID_TO
        )
    )
