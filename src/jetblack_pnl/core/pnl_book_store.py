"""The store interface for book P/L"""

from typing import Protocol

from .book import IBook
from .matched_pool import IMatchedPool
from .security import ISecurity
from .trade import ITrade
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


class IPnlBookStore[SecurityKey, BookKey, TradeKey, Context](Protocol):

    def has(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            context: Context
    ) -> bool:
        ...

    def get(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            context: Context
    ) -> tuple[TradingPnl, IUnmatchedPool[TradeKey, Context], IMatchedPool[TradeKey, Context]]:
        ...

    def set(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            trade: ITrade[TradeKey],
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TradeKey, Context],
            matched: IMatchedPool[TradeKey, Context],
            context: Context
    ) -> None:
        ...
