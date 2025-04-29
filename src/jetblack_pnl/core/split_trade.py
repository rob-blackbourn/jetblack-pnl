"""A split trade
"""

from decimal import Decimal

from .trade import ITrade


class SplitTrade[TradeT: ITrade]:
    """A split trade can or has been split from a larger trade"""

    def __init__(
            self,
            remaining_quantity: Decimal,
            trade: TradeT,
    ) -> None:
        self._remaining_quantity = remaining_quantity
        self._trade = trade

    @property
    def remaining_quantity(self) -> Decimal:
        """The traded quantity"""
        return self._remaining_quantity

    @property
    def trade(self) -> TradeT:
        """The trade"""
        return self._trade

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, SplitTrade) and
            value.remaining_quantity == self.remaining_quantity and
            value.trade == self.trade
        )

    def __repr__(self) -> str:
        side = 'buy' if self.remaining_quantity >= 0 else 'sell'
        return f"{side} {abs(self.remaining_quantity)} of trade: {self.trade}"
