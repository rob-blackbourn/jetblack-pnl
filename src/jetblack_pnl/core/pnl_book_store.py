"""The store interface for book P/L"""

from typing import Protocol

from .book import IBook
from .matched_pool import IMatchedPool
from .security import ISecurity
from .trade import ITrade
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


class IPnlBookStore[TSecurity: ISecurity, TBook: IBook, TTrade: ITrade, TContext](Protocol):

    def has(
            self,
            security: TSecurity,
            book: TBook,
            context: TContext
    ) -> bool:
        ...

    def get(
            self,
            security: TSecurity,
            book: TBook,
            context: TContext
    ) -> tuple[TradingPnl, IUnmatchedPool[TTrade, TContext], IMatchedPool[TTrade, TContext]]:
        ...

    def set(
            self,
            security: TSecurity,
            book: TBook,
            trade: TTrade,
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TTrade, TContext],
            matched: IMatchedPool[TTrade, TContext],
            context: TContext
    ) -> None:
        ...
