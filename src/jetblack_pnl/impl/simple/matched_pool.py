"""A simple implementation of a matched pool"""

from decimal import Decimal
from typing import Sequence


from ...core import IMatchedPool

from .types import Context
from .trade import Trade


class MatchedPool(IMatchedPool[Trade, Context]):
    """Simple pool of matched trades"""

    def __init__(
            self,
            pool: Sequence[
                tuple[Decimal, Trade, Trade]
            ] = ()
    ) -> None:
        self._pool = pool

    def append(
            self,
            closing_quantity: Decimal,
            opening_trade: Trade,
            closing_trade: Trade,
            context: Context
    ) -> None:
        self._pool = tuple((
            *self._pool,
            (closing_quantity, opening_trade, closing_trade)
        ))

    def pool(
            self,
            context: Context
    ) -> Sequence[tuple[Decimal, Trade, Trade]]:
        """Returns the matched pool"""
        return self._pool

    def __len__(self) -> int:
        return len(self._pool)

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, MatchedPool) and
            value._pool == self._pool
        )

    def __str__(self) -> str:
        return str(self._pool)

    def __repr__(self) -> str:
        return str(self._pool)
