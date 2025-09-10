"""The store interface for book P/L"""

from typing import Protocol

from .book import IBook
from .security import ISecurity
from .trade import ITrade
from .trading_pnl import TradingPnl


class IPnlBookStore[SecurityT: ISecurity, BookT: IBook, TradeT: ITrade](Protocol):

    def has(
            self,
            security: SecurityT,
            book: BookT,
    ) -> bool:
        ...

    def get(
            self,
            security: SecurityT,
            book: BookT,
    ) -> TradingPnl:
        ...

    def set(
            self,
            security: SecurityT,
            book: BookT,
            trade: TradeT,
            pnl: TradingPnl,
    ) -> None:
        ...
