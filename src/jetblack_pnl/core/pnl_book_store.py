"""The store interface for book P/L"""

from typing import Protocol

from .book import IBook, TBookKey
from .matched_pool import IMatchedPool
from .security import ISecurity, TSecurityKey
from .trade import ITrade, TTradeKey
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


class IPnlBookStore(Protocol[TSecurityKey, TBookKey, TTradeKey]):  # type: ignore

    def has(
            self,
            security: ISecurity[TSecurityKey],
            book: IBook[TBookKey]
    ) -> bool:
        ...

    def get(
            self,
            security: ISecurity[TSecurityKey],
            book: IBook[TBookKey]
    ) -> tuple[TradingPnl, IUnmatchedPool[TTradeKey], IMatchedPool[TTradeKey]]:
        ...

    def set(
            self,
            security: ISecurity[TSecurityKey],
            book: IBook[TBookKey],
            trade: ITrade[TTradeKey],
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TTradeKey],
            matched: IMatchedPool[TTradeKey]
    ) -> None:
        ...
