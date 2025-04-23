"""A security interface
"""

from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class ISecurity[Key](Protocol):
    """A security interface"""

    @property
    def key(self) -> Key:
        """The key for the security"""

    @property
    def contract_size(self) -> Decimal:
        """The contract size for the security"""

    @property
    def is_cash(self) -> bool:
        """True if the security is cash"""
