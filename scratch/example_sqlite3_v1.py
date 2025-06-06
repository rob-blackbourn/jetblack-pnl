"""SQLite example"""

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sqlite3

from jetblack_pnl.impl.sqlite3_v1 import (
    Trade,
    Security,
    Book,
    TradeDb,
    register_handlers,
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


def main(database: str | Path):
    register_handlers()

    database = ensure_database(database)

    con = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    trade_db = TradeDb(con)

    # trade_db.drop()
    trade_db.create_tables()

    apple = Security.create(con, 'AAPL', Decimal(1), False)
    tech = Book.create(con, 'tech')

    # Buy 6 @ 100
    ts = datetime(2000, 1, 1, 9, 0, 0, 0)
    trade = Trade.create(con, ts, apple, tech, 6, 100)
    pnl = trade_db.add_trade(trade.security, trade.book, trade)
    print(pnl)

    # Buy 6 @ 106
    ts += timedelta(seconds=1)
    trade = Trade.create(con, ts, apple, tech, 6, 106)
    pnl = trade_db.add_trade(trade.security, trade.book, trade)
    print(pnl)

    # Buy 6 @ 103
    ts += timedelta(seconds=1)
    trade = Trade.create(con, ts, apple, tech, 6, 103)
    pnl = trade_db.add_trade(trade.security, trade.book, trade)
    print(pnl)

    # Sell 9 @ 105
    ts += timedelta(seconds=1)
    trade = Trade.create(con, ts, apple, tech, -9, 105)
    pnl = trade_db.add_trade(trade.security, trade.book, trade)
    print(pnl)

    # Sell 12 @ 107
    ts += timedelta(seconds=1)
    trade = Trade.create(con, ts, apple, tech, -12, 107)
    pnl = trade_db.add_trade(trade.security, trade.book, trade)
    print(pnl)

    # Buy 3 @ 103
    ts += timedelta(seconds=1)
    trade = Trade.create(con, ts, apple, tech, 3, 103)
    pnl = trade_db.add_trade(trade.security, trade.book, trade)
    print(pnl)

    con.close()


if __name__ == '__main__':
    # DATABASE = ":memory:"
    DATABASE = "tmp/pnl.sqlite"
    main(DATABASE)
