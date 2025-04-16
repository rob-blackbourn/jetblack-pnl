"""The interface for a trade
"""

from decimal import Decimal
from typing import Protocol, TypeVar, runtime_checkable


TTradeData = TypeVar('TTradeData')


@runtime_checkable
class ITrade(Protocol[TTradeData]):  # type: ignore
    """A trade interface"""

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""

    @property
    def price(self) -> Decimal:
        """The price of the trade"""

    @property
    def data(self) -> TTradeData:
        """An extra data associated with the trade"""
