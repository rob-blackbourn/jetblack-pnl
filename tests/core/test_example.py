"""Tests for the simple implementation"""

from jetblack_pnl.core import PnlBook
from jetblack_pnl.impl.simple import (
    MatchedPool,
    UnmatchedPool,
    Security,
    Book,
    Trade,
    PnlBookStore
)


def test_fifo() -> None:
    """Test the FIFO implementation of the SimplePnl class."""

    pnl_book = PnlBook[str, str, int | None, None](
        PnlBookStore(),
        lambda security, book, context: MatchedPool(),
        lambda security, book, context: UnmatchedPool.Fifo()
    )
    tech = Book('tech')
    apple = Security('AAPL', 1000, False)

    # Buy 6 @ 100
    pnl = pnl_book.add_trade(apple, tech, Trade(6, 100), None)
    # (quantity, avg_cost, price, realized, unrealized)
    assert pnl.strip(apple, 100) == (6, 100, 100, 0, 0)

    # Buy 6 @ 106
    pnl = pnl_book.add_trade(apple, tech, Trade(6, 106), None)
    assert pnl.strip(apple, 106) == (12, 103, 106, 0, 36000)

    # Buy 6 @ 103
    pnl = pnl_book.add_trade(apple, tech, Trade(6, 103), None)
    assert pnl.strip(apple, 103) == (18, 103, 103, 0, 0)

    # Sell 9 @ 105
    pnl = pnl_book.add_trade(apple, tech, Trade(-9, 105), None)
    assert pnl.strip(apple, 105) == (9, 104, 105, 27000, 9000)

    # Sell 9 @ 107
    pnl = pnl_book.add_trade(apple, tech, Trade(-9, 107), None)
    assert pnl.strip(apple, 107) == (0, 0, 107, 54000, 0)
