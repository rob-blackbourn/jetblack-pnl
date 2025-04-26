"""Utilities"""

from decimal import Decimal

type AnyNumber = int | float | str | Decimal


def to_decimal(number: AnyNumber) -> Decimal:
    """Convert to a decimal.

    Args:
        number (int | Decimal | str): The value to convert.

    Returns:
        Decimal: The value as a decimal
    """
    return number if isinstance(number, Decimal) else Decimal(number)


MAX_VALID_TO = 2 ** 63 - 1
