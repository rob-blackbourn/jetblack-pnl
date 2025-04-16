"""A P/L strip
"""

from decimal import Decimal
from typing import NamedTuple


class PnlStrip(NamedTuple):
    quantity: Decimal
    avg_cost: Decimal
    price: Decimal
    realized: Decimal
    unrealized: Decimal
