"""A simple trade implementation"""

from decimal import Decimal

from ...core import ITrade

from .utils import to_decimal


class Trade(ITrade[int | None]):
    """A simple trade"""

    def __init__(
            self,
            quantity: Decimal | int | str,
            price: Decimal | int | str,
            key: int | None = None
    ) -> None:
        self._quantity = to_decimal(quantity)
        self._price = to_decimal(price)
        self._key = key

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    @property
    def key(self) -> int | None:
        return self._key

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Trade) and
            value.quantity == self.quantity and
            value.price == self.price and
            value.key == self.key
        )

    def __repr__(self) -> str:
        prefix = "" if self._key is None else f"[{self._key}]: "
        side = "buy" if self.quantity > 0 else "sell"
        return f"{prefix}{side} {abs(self.quantity)} @ {self.price}"
