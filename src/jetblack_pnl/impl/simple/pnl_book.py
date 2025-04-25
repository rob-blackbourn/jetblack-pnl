from decimal import Decimal

from ...core import PnlBook, TradingPnl

from .book import Book
from .matched_pool import MatchedPool
from .pnl_book_store import PnlBookStore
from .security import Security
from .trade import Trade
from .types import Context
from .unmatched_pools import UnmatchedPool


class SimplePnlBook(PnlBook[Security, Book, Trade, Context]):

    def __init__(self):
        super().__init__(
            PnlBookStore(),
            lambda security, book, context: MatchedPool(),
            lambda security, book, context: UnmatchedPool.Fifo()
        )

    def add(
        self,
        security: Security,
        book: Book,
        quantity: int | Decimal | str,
        price: int | Decimal | str,
    ) -> TradingPnl:
        return self.add_trade(
            security,
            book,
            Trade(quantity, price),
            None
        )
