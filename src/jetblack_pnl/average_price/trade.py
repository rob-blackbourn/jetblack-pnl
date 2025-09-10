"""The interface for a trade
"""

from decimal import Decimal
from typing import Protocol


class ITrade[KeyT](Protocol):
    """A trade interface"""

    @property
    def key(self) -> KeyT:
        """A unique id for the trade"""

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""

    @property
    def price(self) -> Decimal:
        """The price of the trade"""
