"""A simple implementation for demonstrating and testing the P&L algorithm"""

from decimal import Decimal

from ...core.types import IMarketTrade


class MarketTrade(IMarketTrade):
    """A simple trade"""

    def __init__(self, quantity: Decimal | int, price: Decimal | int) -> None:
        self._quantity = Decimal(quantity)
        self._price = Decimal(price)

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, MarketTrade) and
            value.quantity == self.quantity and
            value.price == self.price
        )

    def __repr__(self) -> str:
        return f"{self.quantity} @ {self.price}"
