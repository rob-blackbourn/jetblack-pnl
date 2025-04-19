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
            trade_key: int | None = None
    ) -> None:
        self._quantity = to_decimal(quantity)
        self._price = to_decimal(price)
        self._trade_key = trade_key

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    @property
    def trade_key(self) -> int | None:
        return self._trade_key

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Trade) and
            value.quantity == self.quantity and
            value.price == self.price and
            value.trade_key == self.trade_key
        )

    def __repr__(self) -> str:
        prefix = "" if self._trade_key is None else f"[{self._trade_key}]: "
        side = "buy" if self.quantity > 0 else "sell"
        return f"{prefix}{side} {abs(self.quantity)} @ {self.price}"
