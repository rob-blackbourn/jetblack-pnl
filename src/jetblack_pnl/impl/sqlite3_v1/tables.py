"""SQL statements"""

from sqlite3 import Cursor


def create_table_security(cur: Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS security
        (
            security_id     INTEGER         PRIMARY KEY,
            name            VARCHAR(32)     NOT NULL,
            contract_size   DECIMAL(12, 0)  NOT NULL,
            is_cash         BOOLEAN         NOT NULL,

            UNIQUE (name)
        )
        """
    )


def create_table_book(cur: Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS book
        (
            book_id INTEGER     PRIMARY KEY,
            name    VARCHAR(32) NOT NULL
        )
        """
    )


def create_table_pnl(cur: Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pnl
        (
            security_id INT             NOT NULL,
            book_id     INT             NOT NULL,
            quantity    DECIMAL(12, 0)  NOT NULL,
            cost        DECIMAL(18, 6)  NOT NULL,
            realized    DECIMAL(18, 6)  NOT NULL,

            valid_from  DATETIME        NOT NULL,
            valid_to    DATETIME        NOT NULL,

            PRIMARY KEY(valid_from, valid_to, security_id, book_id)
            FOREIGN KEY (security_id) REFERENCES security(security_id),
            FOREIGN KEY (book_id) REFERENCES book(book_id)
        )
        """
    )


def create_table_trade(cur: Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS trade
        (
            trade_id    INTEGER         PRIMARY KEY,
            timestamp   DATETIME        NOT NULL,
            security_id INT             NOT NULL,
            book_id     TEXT            NOT NULL,
            quantity    DECIMAL         NOT NULL,
            price       DECIMAL         NOT NULL,

            FOREIGN KEY (security_id) REFERENCES security(security_id),
            FOREIGN KEY (book_id) REFERENCES book(book_id)
        );
        """
    )


def create_table_unmatched_trade(cur: Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS unmatched_trade
        (
            trade_id    INTEGER         NOT NULL,
            quantity    DECIMAL         NOT NULL,

            valid_from  DATETIME        NOT NULL,
            valid_to    DATETIME        NOT NULL,

            PRIMARY KEY (valid_from, valid_to, trade_id, quantity),
            FOREIGN KEY (trade_id) REFERENCES trade(trade_id)
        );
        """
    )


def create_table_matched_trade(cur: Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS matched_trade
        (
            opening_trade_id    INTEGER     NOT NULL,
            closing_trade_id    INTEGER     NOT NULL,

            valid_from          DATETIME    NOT NULL,
            valid_to            DATETIME    NOT NULL,

            PRIMARY KEY(valid_from, valid_to, opening_trade_id, closing_trade_id),

            FOREIGN KEY (opening_trade_id) REFERENCES trade(trade_id),
            FOREIGN KEY (closing_trade_id) REFERENCES trade(trade_id)
        );
        """
    )


def create_tables(cur: Cursor) -> None:
    create_table_security(cur)
    create_table_book(cur)
    create_table_pnl(cur)
    create_table_trade(cur)
    create_table_unmatched_trade(cur)
    create_table_matched_trade(cur)


def drop_tables(cur: Cursor) -> None:
    cur.execute("DROP TABLE matched_trade;")
    cur.execute("DROP TABLE unmatched_trade;")
    cur.execute("DROP TABLE trade;")
    cur.execute("DROP TABLE pnl;")
    cur.execute("DROP TABLE book;")
    cur.execute("DROP TABLE security;")
