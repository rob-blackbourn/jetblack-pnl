"""A simple implementation for demonstrating and testing the P&L algorithm"""

from typing import Sequence


from ...core.types import PnlTrade, IMatchedPool


class MatchedPool(IMatchedPool):
    """Simple pool of matched trades"""

    def __init__(self, pool: Sequence[tuple[PnlTrade, PnlTrade]] = ()) -> None:
        self._pool = pool

    def push(self, opening: PnlTrade, closing: PnlTrade) -> None:
        matched_trade = (opening, closing)
        self._pool = tuple((*self._pool, matched_trade))

    def __len__(self) -> int:
        return len(self._pool)

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, MatchedPool) and
            value._pool == self._pool
        )

    def __str__(self) -> str:
        return str(self._pool)
