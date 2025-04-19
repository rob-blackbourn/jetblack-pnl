"""A split trade
"""

from decimal import Decimal
from typing import Generic

from .trade import TTradeKey, ITrade


class SplitTrade(Generic[TTradeKey]):
    """A split trade can or has been split from a larger trade"""

    def __init__(
            self,
            quantity: Decimal,
            trade: ITrade[TTradeKey],
    ) -> None:
        self._quantity = quantity
        self._trade = trade

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""
        return self._quantity

    @property
    def trade(self) -> ITrade[TTradeKey]:
        """The trade"""
        return self._trade

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, SplitTrade) and
            value.quantity == self.quantity and
            value.trade == self.trade
        )

    def __repr__(self) -> str:
        return f"{self.quantity=} <{self.trade=}>"
