"""A split trade
"""

from decimal import Decimal
from typing import Generic

from .trade import TTradeData, ITrade


class SplitTrade(Generic[TTradeData]):
    """A split trade can or has been split from a larger trade"""

    def __init__(
            self,
            quantity: Decimal,
            trade: ITrade[TTradeData],
    ) -> None:
        self._quantity = quantity
        self._trade = trade

    @property
    def quantity(self) -> Decimal:
        """The traded quantity"""
        return self._quantity

    @property
    def trade(self) -> ITrade[TTradeData]:
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
