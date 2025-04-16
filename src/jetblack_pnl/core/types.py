"""Common types
"""

from abc import abstractmethod
from decimal import Decimal
from typing import Generic, NamedTuple, Protocol, TypeVar, runtime_checkable

TSecurityKey = TypeVar('TSecurityKey', covariant=True)


class ISecurity(Protocol[TSecurityKey]):
    """A security interface"""

    @property
    def key(self) -> TSecurityKey:
        """The key for the security"""

    @property
    def contract_size(self) -> Decimal:
        """The contract size for the security"""

    @property
    def is_cash(self) -> bool:
        """True if the security is cash"""


TBookKey = TypeVar('TBookKey', covariant=True)


class IBook(Protocol[TBookKey]):
    """A book interface"""

    @property
    def key(self) -> TBookKey:
        """The key for the book"""


TTradeData = TypeVar('TTradeData')


@runtime_checkable
class ITrade(Protocol[TTradeData]):  # type: ignore

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""

    @property
    def price(self) -> Decimal:
        """The price of the trade"""

    @property
    def data(self) -> TTradeData:
        """An extra data associated with the trade"""


class SplitTrade(Generic[TTradeData]):

    def __init__(
            self,
            quantity: Decimal,
            trade: ITrade[TTradeData],
    ) -> None:
        self._quantity = quantity
        self._trade = trade

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""
        return self._quantity

    @property
    def trade(self) -> ITrade[TTradeData]:
        """The trade"""
        return self._trade

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, SplitTrade) and
            value.quantity == self.quantity and
            value.trade == self.trade
        )

    def __repr__(self) -> str:
        return f"{self.quantity=} <{self.trade=}>"


class IUnmatchedPool(Protocol[TTradeData]):
    """A pool of unmatched trades"""

    @abstractmethod
    def append(self, opening: SplitTrade[TTradeData]) -> None:
        ...

    @abstractmethod
    def insert(self, opening: SplitTrade[TTradeData]) -> None:
        ...

    @abstractmethod
    def pop(self, closing: SplitTrade[TTradeData]) -> SplitTrade[TTradeData]:
        ...

    @abstractmethod
    def has(self, closing: SplitTrade[TTradeData]) -> bool:
        ...


class IMatchedPool(Protocol[TTradeData]):

    @abstractmethod
    def append(
        self,
        opening: SplitTrade[TTradeData],
        closing: SplitTrade[TTradeData]
    ) -> None:
        ...


class PnlStrip(NamedTuple):
    quantity: Decimal
    avg_cost: Decimal
    price: Decimal
    realized: Decimal
    unrealized: Decimal


class TradingPnl(NamedTuple):
    quantity: Decimal
    cost: Decimal
    realized: Decimal

    def avg_cost(self, security: ISecurity[TSecurityKey]) -> Decimal:
        return (
            Decimal(0)
            if self.quantity == 0 else
            -self.cost / self.quantity / security.contract_size
        )

    def unrealized(
            self,
            security: ISecurity[TSecurityKey],
            price: Decimal | int
    ) -> Decimal:
        return self.quantity * security.contract_size * price + self.cost

    def strip(
            self,
            security: ISecurity[TSecurityKey],
            price: Decimal | int
    ) -> PnlStrip:
        return PnlStrip(
            self.quantity,
            self.avg_cost(security),
            Decimal(price),
            self.realized,
            self.unrealized(security, price)
        )
