from typing import TypeAlias

from ...core import (
    IPnlBookStore,
    TradingPnl,
    IUnmatchedPool,
    IMatchedPool,
    ISecurity,
    IBook
)

SecurityKey: TypeAlias = str
BookKey: TypeAlias = str
TradeKey: TypeAlias = int | None


class PnlBookStore(IPnlBookStore[str, str, int | None]):

    def __init__(self) -> None:
        self._cache: dict[
            tuple[SecurityKey, BookKey],
            tuple[TradingPnl, IUnmatchedPool[TradeKey], IMatchedPool[TradeKey]]
        ] = {}

    def has(
            self,
            security: ISecurity[str],
            book: IBook[str]
    ) -> bool:
        key = (security.key, book.key)
        return key in self._cache

    def get(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey]
    ) -> tuple[TradingPnl, IUnmatchedPool[TradeKey], IMatchedPool[TradeKey]]:
        key = (security.key, book.key)
        return self._cache[key]

    def set(
            self,
            security: ISecurity[SecurityKey],
            book: IBook[BookKey],
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[TradeKey],
            matched: IMatchedPool[TradeKey]
    ) -> None:
        key = (security.key, book.key)
        self._cache[key] = (pnl, unmatched, matched)
