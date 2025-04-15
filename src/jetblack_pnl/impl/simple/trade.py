"""A simple trade implementation"""

from decimal import Decimal

from ...core.types import ITrade

from .utils import to_decimal


class Trade(ITrade):
    """A simple trade"""

    def __init__(
            self,
            quantity: Decimal | int | str,
            price: Decimal | int | str
    ) -> None:
        self._quantity = to_decimal(quantity)
        self._price = to_decimal(price)

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Trade) and
            value.quantity == self.quantity and
            value.price == self.price
        )

    def __repr__(self) -> str:
        return f"{self.quantity} @ {self.price}"
