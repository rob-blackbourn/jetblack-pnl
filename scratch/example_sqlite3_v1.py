"""SQLite example"""

from datetime import datetime, timedelta
import sqlite3

from jetblack_pnl.impl.sqlite3_v1 import TradeDb, register_handlers


def main():
    register_handlers()
    con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)

    trade_db = TradeDb(con)

    # trade_db.drop()
    trade_db.create_tables()

    ticker = 'AAPL'
    book = 'tech'

    # Buy 6 @ 100
    ts = datetime(2000, 1, 1, 9, 0, 0, 0)
    pnl = trade_db.add_trade(ts, ticker, 6, 100, book)
    print(pnl)

    # Buy 6 @ 106
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, ticker, 6, 106, book)
    print(pnl)

    # Buy 6 @ 103
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, ticker, 6, 103, book)
    print(pnl)

    # Sell 9 @ 105
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, ticker, -9, 105, book)
    print(pnl)

    # Sell 9 @ 107
    ts += timedelta(seconds=1)
    pnl = trade_db.add_trade(ts, ticker, -9, 107, book)
    print(pnl)

    con.close()


if __name__ == '__main__':
    main()
