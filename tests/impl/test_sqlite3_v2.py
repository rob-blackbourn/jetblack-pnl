"""SQLite example"""

from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
import sqlite3
from typing import Generator

from jetblack_pnl.core import SplitTrade
from jetblack_pnl.impl.sqlite3_v2 import (
    create_tables,
    register_handlers,
    Trade,
    Security,
    Book,
    DbPnlBook
)


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


def test_sqlite3_v2() -> None:
    register_handlers()

    with sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES) as con:
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
            _, unmatched, matched = pnl_book.get(apple, tech, cur)
            assert pnl == (6, -600, 0)
            assert unmatched.pool(cur) == (
                SplitTrade(Decimal(6), trade),
            )
            assert matched.pool(cur) == ()

        # Buy 6 @ 106
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 6, 106)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        assert pnl == (12, -1236, 0)

        # Buy 6 @ 103
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 6, 103)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        assert pnl == (18, -1854, 0)

        # Sell 9 @ 105
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, -9, 105)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        assert pnl == (9, -936, 27)

        # Sell 12 @ 107
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, -12, 107)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        assert pnl == (-3, 321, 54)

        # Buy 3 @ 103
        ts += timedelta(seconds=1)
        trade = Trade.create(con, ts, apple, tech, 3, 103)
        with cursor(con) as cur:
            pnl = pnl_book.add_trade(apple, tech, trade, cur)
        assert pnl == (0, 0, 66)
