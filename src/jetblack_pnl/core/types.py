"""Common types
"""

from abc import abstractmethod
from decimal import Decimal
from typing import NamedTuple, Protocol, TypeVar, runtime_checkable

TSecurityKey = TypeVar('TSecurityKey', covariant=True)


class ISecurity(Protocol[TSecurityKey]):
    """A security interface"""

    @property
    def key(self) -> TSecurityKey:
        """The key for the security"""

    @property
    def contract_size(self) -> Decimal:
        """The contract size for the security"""


TBookKey = TypeVar('TBookKey', covariant=True)


class IBook(Protocol[TBookKey]):
    """A book interface"""

    @property
    def key(self) -> TBookKey:
        """The key for the book"""


@runtime_checkable
class ITrade(Protocol):

    @property
    @abstractmethod
    def quantity(self) -> Decimal:
        ...

    @property
    @abstractmethod
    def price(self) -> Decimal:
        ...


class SplitTrade(NamedTuple):
    quantity: Decimal
    trade: ITrade


class IUnmatchedPool(Protocol):

    @abstractmethod
    def push(self, opening: SplitTrade) -> None:
        ...

    @abstractmethod
    def pop(self, closing: SplitTrade) -> SplitTrade:
        ...

    @abstractmethod
    def has(self, closing: SplitTrade) -> bool:
        ...


class IMatchedPool(Protocol):

    @abstractmethod
    def push(self, opening: SplitTrade, closing: SplitTrade) -> None:
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

    @property
    def avg_cost(self) -> Decimal:
        return Decimal(0) if self.quantity == 0 else -self.cost / self.quantity

    def unrealized(self, price: Decimal | int) -> Decimal:
        return self.quantity * price + self.cost

    def strip(self, price: Decimal | int) -> PnlStrip:
        return PnlStrip(
            self.quantity,
            self.avg_cost,
            Decimal(price),
            self.realized,
            self.unrealized(price)
        )
