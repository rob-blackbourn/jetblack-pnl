
from ...core import (
    IPnlBookStore,
    TradingPnl,
    IUnmatchedPool,
    IMatchedPool,
)

from .book import Book
from .security import Security
from .trade import Trade
from .types import Context


class PnlBookStore(IPnlBookStore[Security, Book, Trade, Context]):

    def __init__(self) -> None:
        self._cache: dict[
            tuple[str, str],
            tuple[
                TradingPnl,
                IUnmatchedPool[Trade, Context],
                IMatchedPool[Trade, Context]
            ]
        ] = {}

    def has(
            self,
            security: Security,
            book: Book,
            context: Context
    ) -> bool:
        key = (security.key, book.key)
        return key in self._cache

    def get(
            self,
            security: Security,
            book: Book,
            context: Context
    ) -> tuple[TradingPnl, IUnmatchedPool[Trade, Context], IMatchedPool[Trade, Context]]:
        key = (security.key, book.key)
        return self._cache[key]

    def set(
            self,
            security: Security,
            book: Book,
            trade: Trade,
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[Trade, Context],
            matched: IMatchedPool[Trade, Context],
            context: Context
    ) -> None:
        key = (security.key, book.key)
        self._cache[key] = (pnl, unmatched, matched)
