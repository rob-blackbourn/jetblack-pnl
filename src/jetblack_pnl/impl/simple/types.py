"""Types for the simple implementation"""

from decimal import Decimal
from typing import Protocol, TypeVar

TSecurityKey = TypeVar('TSecurityKey', covariant=True)


class ISecurity(Protocol[TSecurityKey]):
    """A security interface"""

    @property
    def key(self) -> TSecurityKey:
        """The key for the security"""

    @property
    def contract_size(self) -> Decimal:
        """The contract size for the security"""
