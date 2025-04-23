"""A class to hold the trading P/L.
"""

from decimal import Decimal
from typing import NamedTuple


from .security import ISecurity
from .pnl_strip import PnlStrip


class TradingPnl(NamedTuple):
    quantity: Decimal
    cost: Decimal
    realized: Decimal

    def avg_cost[SecurityKey](self, security: ISecurity[SecurityKey]) -> Decimal:
        return (
            Decimal(0)
            if self.quantity == 0 else
            -self.cost / self.quantity / security.contract_size
        )

    def unrealized[SecurityKey](
            self,
            security: ISecurity[SecurityKey],
            price: Decimal | int
    ) -> Decimal:
        return self.quantity * security.contract_size * price + self.cost

    def strip[SecurityKey](
            self,
            security: ISecurity[SecurityKey],
            price: Decimal | int
    ) -> PnlStrip:
        return PnlStrip(
            self.quantity,
            self.avg_cost(security),
            Decimal(price),
            self.realized,
            self.unrealized(security, price)
        )

    def __repr__(self) -> str:
        return f"position: {self.quantity}, cost: {self.cost}, realized: {self.realized}"
