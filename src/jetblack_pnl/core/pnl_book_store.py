"""The store interface for book P/L"""

from typing import Protocol

from .book import IBook
from .matched_pool import IMatchedPool
from .security import ISecurity
from .trade import ITrade
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


class IPnlBookStore[SecurityT: ISecurity, BookT: IBook, TradeT: ITrade, ContextT](Protocol):

    def has(
            self,
            security: SecurityT,
            book: BookT,
            context: ContextT
    ) -> bool:
        ...

    def get(
            self,
            security: SecurityT,
            book: BookT,
            context: ContextT
    ) -> tuple[TradingPnl, IUnmatchedPool[TradeT, ContextT], IMatchedPool[TradeT, ContextT]]:
        ...

    def set(
            self,
            security: SecurityT,
            book: BookT,
            trade: TradeT,
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TradeT, ContextT],
            matched: IMatchedPool[TradeT, ContextT],
            context: ContextT
    ) -> None:
        ...
