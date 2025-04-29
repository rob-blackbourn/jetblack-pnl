"""SQLite example"""

from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sqlite3
from sqlite3 import Cursor
from typing import Generator

from jetblack_pnl.core import TradingPnl, IMatchedPool, IUnmatchedPool
from jetblack_pnl.impl.sqlite3_v2 import (
    create_tables,
    register_handlers,
    Trade,
    Security,
    Book,
    DbPnlBook,
)


def ensure_database(database: str | Path, truncate: bool) -> str | Path:
    if isinstance(database, str):
        if database == ':memory:':
            return ':memory:'
        database = Path(database)

    if database.exists():
        if truncate:
            database.unlink()
        else:
            raise FileExistsError(f"Database exists: {database}")

    if not database.parent.exists():
        database.parent.mkdir()

    return database


@contextmanager
def cursor(con: sqlite3.Connection) -> Generator[sqlite3.Cursor, None, None]:
    cur = con.cursor()
    try:
        yield cur
    except:
        con.rollback()
        raise
    finally:
        cur.close()


def display(
        pnl_book: DbPnlBook,
        security: Security,
        book: Book,
        context: Cursor
) -> None:
    pnl, unmatched, matched = pnl_book.get(security, book, context)
    avg_cost = -pnl.cost / pnl.quantity if pnl.quantity != 0 else 0
    text = f"pnl: {pnl}, avg_cost: {avg_cost}" + "\n"
    text += "matched:\n"
    if not matched.pool(context):
        text += "    None\n"
    else:
        for quantity, opening, closing in matched.pool(context):
            text += f"    ({opening}) matches ({abs(quantity)} of {closing})" + "\n"
    text += "unmatched:\n"
    if not unmatched.pool(context):
        text += "    None\n"
    else:
        for trade in unmatched.pool(context):
            text += f"    {trade}" + "\n"
    print(text)


def main(database: str | Path):
    register_handlers()

    database = ensure_database(database, truncate=True)

    with sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        pnl_book = DbPnlBook()

        # book.drop()
        create_tables(con.cursor())

        apple = Security.create(con, 'AAPL', Decimal(1), False)
        tech = Book.create(con, 'tech')

        # Buy 6 @ 100
        ts = datetime(2000, 1, 1, 9, 0, 0, 0)
        trade = Trade.create(con, ts, apple, tech, 6, 100)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
            assert pnl == (6, -600, 0)
            display(pnl_book, apple, tech, cur)

        # Buy 6 @ 106
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 6, 106)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
            assert pnl == (12, -1236, 0)
            display(pnl_book, apple, tech, cur)

        # Buy 6 @ 103
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 6, 103)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
            assert pnl == (18, -1854, 0)
            display(pnl_book, apple, tech, cur)

        # Sell 9 @ 105
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, -9, 105)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
            assert pnl == (9, -936, 27)
            display(pnl_book, apple, tech, cur)

        # Sell 12 @ 107
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, -12, 107)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
            assert pnl == (-3, 321, 54)
            display(pnl_book, apple, tech, cur)

        # Buy 3 @ 103
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 3, 103)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
            assert pnl == (0, 0, 66)
            display(pnl_book, apple, tech, cur)


if __name__ == '__main__':
    # DATABASE = ":memory:"
    DATABASE = "tmp/pnl.sqlite"
    main(DATABASE)
