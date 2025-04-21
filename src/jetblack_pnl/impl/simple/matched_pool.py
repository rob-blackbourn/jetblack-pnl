"""A simple implementation of a matched pool"""

from typing import Sequence, TypeAlias


from ...core import SplitTrade, IMatchedPool

TradeKey: TypeAlias = int | None


class MatchedPool(IMatchedPool[TradeKey]):
    """Simple pool of matched trades"""

    def __init__(
            self,
            pool: Sequence[
                tuple[SplitTrade[TradeKey], SplitTrade[TradeKey]]
            ] = ()
    ) -> None:
        self._pool = pool

    def append(
            self,
            opening: SplitTrade[TradeKey],
            closing: SplitTrade[TradeKey]
    ) -> None:
        matched_trade = (opening, closing)
        self._pool = tuple((*self._pool, matched_trade))

    @property
    def pool(
            self
    ) -> Sequence[tuple[SplitTrade[TradeKey], SplitTrade[TradeKey]]]:
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
