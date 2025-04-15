"""A simple implementation for demonstrating and testing the P&L algorithm"""

from decimal import Decimal


def to_decimal(number: int | Decimal) -> Decimal:
    return number if isinstance(number, Decimal) else Decimal(number)
