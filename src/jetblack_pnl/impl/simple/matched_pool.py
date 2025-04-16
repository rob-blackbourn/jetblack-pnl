"""A simple implementation of a matched pool"""

from typing import Sequence


from ...core import SplitTrade, IMatchedPool


class MatchedPool(IMatchedPool):
    """Simple pool of matched trades"""

    def __init__(self, pool: Sequence[tuple[SplitTrade, SplitTrade]] = ()) -> None:
        self._pool = pool

    def append(self, opening: SplitTrade, closing: SplitTrade) -> None:
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
