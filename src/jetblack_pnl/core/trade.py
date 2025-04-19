"""The interface for a trade
"""

from decimal import Decimal
from typing import Protocol, TypeVar, runtime_checkable

TTradeKey = TypeVar('TTradeKey')


@runtime_checkable
class ITrade(Protocol[TTradeKey]):  # type: ignore
    """A trade interface"""

    @property
    def key(self) -> TTradeKey:
        """A unique id for the trade"""

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""

    @property
    def price(self) -> Decimal:
        """The price of the trade"""
