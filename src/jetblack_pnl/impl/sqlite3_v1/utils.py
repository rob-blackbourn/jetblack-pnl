"""Utilities"""

from decimal import Decimal


def to_decimal(number: int | Decimal | str) -> Decimal:
    """Convert to a decimal.

    Args:
        number (int | Decimal | str): The value to convert.

    Returns:
        Decimal: The value as a decimal
    """
    return number if isinstance(number, Decimal) else Decimal(number)


MAX_VALID_TO = 2 ** 32 - 1
