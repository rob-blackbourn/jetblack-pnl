"""A simple implementation of a security"""

from decimal import Decimal

from ...core import ISecurity
from .utils import to_decimal


class Security(ISecurity[str]):
    """A simple implementation of a security"""

    def __init__(
            self,
            key: str,
            contract_size: int | Decimal | str,
            is_cash: bool
    ) -> None:
        self._key = key
        self._contract_size = to_decimal(contract_size)
        self._is_cash = is_cash

    @property
    def key(self) -> str:
        return self._key

    @property
    def contract_size(self) -> Decimal:
        return self._contract_size

    @property
    def is_cash(self) -> bool:
        return self._is_cash
