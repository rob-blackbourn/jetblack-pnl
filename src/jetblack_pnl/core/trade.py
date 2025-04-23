"""The interface for a trade
"""

from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class ITrade[Key](Protocol):  # type: ignore
    """A trade interface"""

    @property
    def key(self) -> Key:
        """A unique id for the trade"""

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""

    @property
    def price(self) -> Decimal:
        """The price of the trade"""
