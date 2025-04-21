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

SecurityKey: TypeAlias = str
BookKey: TypeAlias = str
TradeKey: TypeAlias = int | None
Context: TypeAlias = None

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
            security: ISecurity[str],
            book: IBook[str],
            context: None
    ) -> bool:
        key = (security.key, book.key)
        return key in self._cache

    def get(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            context: None
    ) -> tuple[TradingPnl, UnmatchedPool, MatchedPool]:
        key = (security.key, book.key)
        return self._cache[key]

    def set(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            trade: ITrade,
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TradeKey, None],
            matched: IMatchedPool[TradeKey, None],
            context: None
    ) -> None:
        key = (security.key, book.key)
        self._cache[key] = (pnl, unmatched, matched)
