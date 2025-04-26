"""SQLite example"""

from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sqlite3
from typing import Any, Generator

from jetblack_pnl.impl.sqlite3_v2 import (
    create_tables,
    register_handlers,
    Trade,
    Security,
    Book,
    DbPnlBook
)


def ensure_database(database: str | Path) -> str | Path:
    if isinstance(database, str):
        if database == ':memory:':
            return ':memory:'
        database = Path(database)

    if database.exists():
        database.unlink()
        # raise FileExistsError(f"Database exists: {database}")

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


def main(database: str | Path):
    register_handlers()

    database = ensure_database(database)

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
        print(pnl)

        # Buy 6 @ 106
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 6, 106)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        print(pnl)

        # Buy 6 @ 103
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 6, 103)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        print(pnl)

        # Sell 9 @ 105
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, -9, 105)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        print(pnl)

        # Sell 12 @ 107
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, -12, 107)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        print(pnl)

        # Buy 3 @ 103
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 3, 103)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        print(pnl)


if __name__ == '__main__':
    DATABASE = ":memory:"
    # DATABASE = "tmp/pnl.sqlite"
    main(DATABASE)
