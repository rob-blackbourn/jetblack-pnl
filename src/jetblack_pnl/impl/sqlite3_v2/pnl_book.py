"""A basic database implementation"""

from sqlite3 import Cursor

from ...core import TradingPnl, PnlBook

from .book import Book
from .matched_pool import MatchedPool
from .security import Security
from .trade import Trade
from .unmatched_pools import UnmatchedPool
from .pnl_book_store import PnlBookStore


class DbPnlBook(PnlBook[Security, Book, Trade, Cursor]):

    def __init__(self) -> None:
        super().__init__(
            PnlBookStore(),
            lambda security, book, context: MatchedPool(security, book),
            lambda security, book, context: UnmatchedPool.Fifo(security, book),
        )
        self._pnl: dict[tuple[int, int], TradingPnl] = {}
