"""Tests for the simple implementation"""

from jetblack_pnl.impl.simple import (
    PnlBook,
    MatchedPool,
    UnmatchedPool,
    Security,
    Book
)


def test_fifo() -> None:
    """Test the FIFO implementation of the SimplePnl class."""

    pnl_book = PnlBook[str, str](MatchedPool, UnmatchedPool.Fifo)
    tech = Book('tech')
    apple = Security('AAPL', 1000)

    # Buy 6 @ 100
    pnl = pnl_book.add_trade(apple, tech, 6, 100)
    # (quantity, avg_cost, price, realized, unrealized)
    assert pnl.strip(100) == (6, 100, 100, 0, 0)

    # Buy 6 @ 106
    pnl = pnl_book.add_trade(apple, tech, 6, 106)
    assert pnl.strip(106) == (12, 103, 106, 0, 36)

    # Buy 6 @ 103
    pnl = pnl_book.add_trade(apple, tech, 6, 103)
    assert pnl.strip(103) == (18, 103, 103, 0, 0)

    # Sell 9 @ 105
    pnl = pnl_book.add_trade(apple, tech, -9, 105)
    assert pnl.strip(105) == (9, 104, 105, 27, 9)

    # Sell 9 @ 107
    pnl = pnl_book.add_trade(apple, tech, -9, 107)
    assert pnl.strip(107) == (0, 0, 107, 54, 0)
