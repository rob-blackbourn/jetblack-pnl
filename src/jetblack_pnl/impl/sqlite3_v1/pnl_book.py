"""A basic database implementation"""

from sqlite3 import Connection

from ...core import (
    TradingPnl,
    ISecurity,
    IBook,
    IMatchedPool,
    IUnmatchedPool,
    PnlBook
)

from .matched_pool import MatchedPool
from .unmatched_pool import UnmatchedPool
from .tables import create_tables, drop_tables
from .pnl_book_store import PnlBookStore


class DbPnlBook(PnlBook[int, int, int]):

    def __init__(self, con: Connection) -> None:
        self._con = con
        super().__init__(
            PnlBookStore(con),
            self._make_matched,
            self._make_unmatched
        )
        self._pnl: dict[tuple[int, int], TradingPnl] = {}

    def _make_matched(
            self,
            security: ISecurity[int],
            book: IBook[int]
    ) -> IMatchedPool[int]:
        return MatchedPool(self._con.cursor(), security, book)

    def _make_unmatched(
            self,
            security: ISecurity[int],
            book: IBook[int]
    ) -> IUnmatchedPool[int]:
        return UnmatchedPool.Fifo(self._con.cursor(), security, book)

    def create_tables(self) -> None:
        cur = self._con.cursor()
        try:
            create_tables(cur)
        finally:
            cur.close()

    def drop(self) -> None:
        cur = self._con.cursor()
        try:
            drop_tables(cur)
        finally:
            cur.close()
