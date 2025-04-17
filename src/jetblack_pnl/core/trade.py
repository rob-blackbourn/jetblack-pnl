"""The interface for a trade
"""

from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class ITrade(Protocol):
    """A trade interface"""

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""

    @property
    def price(self) -> Decimal:
        """The price of the trade"""
