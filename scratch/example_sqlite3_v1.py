"""SQLite example"""

from datetime import datetime, timedelta
from decimal import Decimal
import sqlite3

from jetblack_pnl.impl.sqlite3_v1 import (
    TradeDb,
    register_handlers,
    Security,
    Book
)


def main(database: str):
    register_handlers()
    con = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    trade_db = TradeDb(con)

    # trade_db.drop()
    trade_db.create_tables()

    security = Security.create(con, 'AAPL', Decimal(1), False)
    book = Book.create(con, 'tech')

    # Buy 6 @ 100
    ts = datetime(2000, 1, 1, 9, 0, 0, 0)
    pnl = trade_db.add_trade(ts, security, book, 6, 100)
    print(pnl)

    # Buy 6 @ 106
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, security, book, 6, 106)
    print(pnl)

    # Buy 6 @ 103
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, security, book, 6, 103)
    print(pnl)

    # Sell 9 @ 105
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, security, book, -9, 105)
    print(pnl)

    # Sell 9 @ 107
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, security, book, -9, 107)
    print(pnl)

    con.close()


if __name__ == '__main__':
    DATABASE = ":memory:"
    main(DATABASE)
