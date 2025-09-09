"""An example using polars"""

from decimal import Decimal
from typing import Sequence

import polars as pl

from jetblack_pnl.core import (
    ITrade,
    ISecurity,
    IBook,
    IMatchedPool,
    IPnlBookStore,
    IUnmatchedPool,
    PnlBook,
    SplitTrade,
    TradingPnl,
)


class Trade(ITrade[str]):

    def __init__(self, key: str, quantity: Decimal, price: Decimal) -> None:
        self._key = key
        self._quantity = quantity
        self._price = price

    @property
    def key(self) -> str:
        return self._key

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price


class Security(ISecurity[str]):

    def __init__(self, key: str, contract_size: Decimal) -> None:
        self._key = key
        self._contract_size = contract_size
        self._is_cash = False

    @property
    def key(self) -> str:
        return self._key

    @property
    def contract_size(self) -> Decimal:
        return self._contract_size

    @property
    def is_cash(self) -> bool:
        return self._is_cash


class Book(IBook[str]):

    def __init__(self, key: str) -> None:
        self._key = key

    @property
    def key(self) -> str:
        return self._key


class PnlBookStore(IPnlBookStore[Security, Book, Trade, None]):
    """A simple in-memory implementation of a PnL book store"""

    def __init__(self) -> None:
        self._cache: dict[
            tuple[str, str],
            tuple[
                TradingPnl,
                IUnmatchedPool[Trade, None],
                IMatchedPool[Trade, None]
            ]
        ] = {}

    def has(self, security: Security, book: Book, context: None) -> bool:
        key = (security.key, book.key)
        return key in self._cache

    def get(
            self,
            security: Security,
            book: Book,
            context: None
    ) -> tuple[TradingPnl, IUnmatchedPool[Trade, None], IMatchedPool[Trade, None]]:
        key = (security.key, book.key)
        return self._cache[key]

    def set(
            self,
            security: Security,
            book: Book,
            trade: Trade,
            pnl: TradingPnl,
            unmatched: IUnmatchedPool[Trade, None],
            matched: IMatchedPool[Trade, None],
            context: None
    ) -> None:
        key = (security.key, book.key)
        self._cache[key] = (pnl, unmatched, matched)


class MatchedPool(IMatchedPool[Trade, None]):
    """Simple pool of matched trades"""

    def __init__(
            self,
            pool: Sequence[
                tuple[Decimal, Trade, Trade]
            ] = ()
    ) -> None:
        self._pool = pool

    def append(
            self,
            closing_quantity: Decimal,
            opening_trade: Trade,
            closing_trade: Trade,
            context: None
    ) -> None:
        self._pool = tuple((
            *self._pool,
            (closing_quantity, opening_trade, closing_trade)
        ))

    def pool(
            self,
            context: None
    ) -> Sequence[tuple[Decimal, Trade, Trade]]:
        """Returns the matched pool"""
        return self._pool


class UnmatchedPool(IUnmatchedPool[Trade, None]):

    def __init__(self, pool: Sequence[SplitTrade[Trade]] = ()) -> None:
        self._pool = pool

    def append(self, opening: SplitTrade[Trade], context: None) -> None:
        self._pool = tuple((*self._pool, opening))

    def insert(self, opening: SplitTrade[Trade], context: None) -> None:
        self._pool = tuple((opening, *self._pool))

    def pop(self, _closing: SplitTrade[Trade], context: None) -> SplitTrade[Trade]:
        trade, self._pool = (self._pool[0], self._pool[1:])
        return trade

    def has(self, _closing: SplitTrade[Trade], context: None) -> bool:
        return len(self._pool) > 0

    def pool(self, context: None) -> Sequence[SplitTrade[Trade]]:
        return self._pool


class PolarsPnlBook(PnlBook[Security, Book, Trade, None]):

    def __init__(self):
        super().__init__(
            PnlBookStore(),
            lambda security, book, context: MatchedPool(),
            lambda security, book, context: UnmatchedPool()
        )

    def add_trade(
        self,
        security: Security,
        book: Book,
        trade: Trade,
        context: None
    ) -> TradingPnl:
        return super().add_trade(
            security,
            book,
            trade,
            None
        )


TRADE_SCHEMA = pl.Struct({
    'trade_id': pl.String(),
    'quantity': pl.Decimal(),
    'price': pl.Decimal(),
})

MATCHED_SCHEMA = pl.Struct({
    'closing_quantity': pl.Decimal(),
    'opening_trade': TRADE_SCHEMA,
    'closing_trade': TRADE_SCHEMA,
})

UNMATCHED_SCHEMA = pl.Struct({
    'remaining_quantity': pl.Decimal(),
    'trade': TRADE_SCHEMA,
})

SCHEMA = {
    'trade_id': pl.String(),
    'quantity': pl.Decimal(),
    'price': pl.Decimal(),
    'ticker': pl.String(),
    'contract_size': pl.Decimal(),
    'book': pl.String(),
    'position': pl.Decimal(),
    'cost': pl.Decimal(),
    'realized': pl.Decimal(),
    'unmatched': pl.List(UNMATCHED_SCHEMA),
    'matched': pl.List(MATCHED_SCHEMA),
}


def apply_trades(
        trade_ids: pl.Series,
        quantities: pl.Series,
        prices: pl.Series,
        tickers: pl.Series,
        contract_sizes: pl.Series,
        books: pl.Series,
        positions: pl.Series,
        costs: pl.Series,
        realizeds: pl.Series,
        unmatcheds: pl.Series,
        matcheds: pl.Series,
) -> pl.Series:
    pnl_book = PolarsPnlBook()
    for (
        trade_id,
        quantity,
        price,
        ticker,
        contract_size,
        book,
        position,
        cost,
        realized,
        unmatched,
        matched,
    ) in zip(
        trade_ids,
        quantities,
        prices,
        tickers,
        contract_sizes,
        books,
        positions,
        costs,
        realizeds,
        unmatcheds,
        matcheds,
    ):
        trade = Trade(trade_id, quantity, price)
        security = Security(ticker, contract_size)
        book = Book(book)
        pnl = TradingPnl(position, cost, realized)
        unmatched = UnmatchedPool(unmatched)
        matched = MatchedPool(matched)

    return position


def main() -> None:
    df = pl.DataFrame(
        [
            {
                'trade_id': 'a001',
                'quantity': Decimal(6),
                'price': Decimal(100),
                'ticker': 'AAPL',
                'contract_size': Decimal(1),
                'book': 'TechStocks',
                'position': None,
                'cost': None,
                'realized': None,
                'unmatched': None,
                'matched': None,
            },
            {
                'trade_id': 'a002',
                'quantity': Decimal(6),
                'price': Decimal(106),
                'ticker': 'AAPL',
                'contract_size': Decimal(1),
                'book': 'TechStocks',
                'position': None,
                'cost': None,
                'realized': None,
                'unmatched': None,
                'matched': None,
            },
            {
                'trade_id': 'a003',
                'quantity': Decimal(6),
                'price': Decimal(103),
                'ticker': 'AAPL',
                'contract_size': Decimal(1),
                'book': 'TechStocks',
                'position': None,
                'cost': None,
                'realized': None,
                'unmatched': None,
                'matched': None,
            },
            {
                'trade_id': 'a004',
                'quantity': Decimal(-9),
                'price': Decimal(105),
                'ticker': 'AAPL',
                'contract_size': Decimal(1),
                'book': 'TechStocks',
                'position': None,
                'cost': None,
                'realized': None,
                'unmatched': None,
                'matched': None,
            },
            {
                'trade_id': 'a005',
                'quantity': Decimal(-12),
                'price': Decimal(107),
                'ticker': 'AAPL',
                'contract_size': Decimal(1),
                'book': 'TechStocks',
                'position': None,
                'cost': None,
                'realized': None,
                'unmatched': None,
                'matched': None,
            },
            {
                'trade_id': 'a006',
                'quantity': Decimal(3),
                'price': Decimal(103),
                'ticker': 'AAPL',
                'contract_size': Decimal(1),
                'book': 'TechStocks',
                'position': None,
                'cost': None,
                'realized': None,
                'unmatched': None,
                'matched': None,
            },
        ],
        schema=SCHEMA,
    )
    print(df)

    df2 = df.with_columns(
        pl.struct([
            'trade_id',
            'quantity',
            'price',
            'ticker',
            'contract_size',
            'book',
            'position',
            'cost',
            'realized',
            'unmatched',
            'matched',
        ]).map_batches(
            lambda x: apply_trades(
                x.struct.field('trade_id'),
                x.struct.field('quantity'),
                x.struct.field('price'),
                x.struct.field('ticker'),
                x.struct.field('contract_size'),
                x.struct.field('book'),
                x.struct.field('position'),
                x.struct.field('cost'),
                x.struct.field('realized'),
                x.struct.field('unmatched'),
                x.struct.field('matched'),
            )
        )
    )
    print(df2)


if __name__ == "__main__":
    main()
