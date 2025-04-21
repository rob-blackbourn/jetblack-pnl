"""The store interface for book P/L"""

from typing import Protocol

from .book import IBook, TBookKey
from .context import TContext
from .matched_pool import IMatchedPool
from .security import ISecurity, TSecurityKey
from .trade import ITrade, TTradeKey
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


class IPnlBookStore(Protocol[TSecurityKey, TBookKey, TTradeKey, TContext]):  # type: ignore

    def has(
            self,
            security: ISecurity[TSecurityKey],
            book: IBook[TBookKey],
            context: TContext
    ) -> bool:
        ...

    def get(
            self,
            security: ISecurity[TSecurityKey],
            book: IBook[TBookKey],
            context: TContext
    ) -> tuple[TradingPnl, IUnmatchedPool[TTradeKey, TContext], IMatchedPool[TTradeKey, TContext]]:
        ...

    def set(
            self,
            security: ISecurity[TSecurityKey],
            book: IBook[TBookKey],
            trade: ITrade[TTradeKey],
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TTradeKey, TContext],
            matched: IMatchedPool[TTradeKey, TContext],
            context: TContext
    ) -> None:
        ...
