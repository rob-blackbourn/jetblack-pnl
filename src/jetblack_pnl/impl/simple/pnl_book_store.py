from typing import TypeAlias

from ...core import (
    IPnlBookStore,
    TradingPnl,
    IUnmatchedPool,
    IMatchedPool,
    ISecurity,
    IBook,
    ITrade
)

from .types import SecurityKey, BookKey, TradeKey, Context

UnmatchedPool: TypeAlias = IUnmatchedPool[TradeKey, Context]
MatchedPool: TypeAlias = IMatchedPool[TradeKey, Context]


class PnlBookStore(IPnlBookStore[SecurityKey, BookKey, TradeKey, Context]):

    def __init__(self) -> None:
        self._cache: dict[
            tuple[SecurityKey, BookKey],
            tuple[TradingPnl, UnmatchedPool, MatchedPool]
        ] = {}

    def has(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            context: Context
    ) -> bool:
        key = (security.key, book.key)
        return key in self._cache

    def get(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            context: Context
    ) -> tuple[TradingPnl, UnmatchedPool, MatchedPool]:
        key = (security.key, book.key)
        return self._cache[key]

    def set(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            trade: ITrade,
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TradeKey, Context],
            matched: IMatchedPool[TradeKey, Context],
            context: Context
    ) -> None:
        key = (security.key, book.key)
        self._cache[key] = (pnl, unmatched, matched)
