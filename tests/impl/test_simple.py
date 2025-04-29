"""Tests for the simple implementation"""

from decimal import Decimal

from jetblack_pnl.core import SplitTrade
from jetblack_pnl.impl.simple import Security, Book, Trade, SimplePnlBook


def test_fifo() -> None:
    """Test the FIFO implementation of the SimplePnl class."""

    pnl_book = SimplePnlBook()
    tech = Book('tech')
    apple = Security('AAPL', 1000, False)

    # Buy 6 @ 100
    pnl = pnl_book.add_trade(apple, tech, Trade(6, 100), None)
    # (quantity, avg_cost, price, realized, unrealized)
    assert pnl.strip(apple, 100) == (6, 100, 100, 0, 0)
    _, unmatched, matched = pnl_book.get(apple, tech, None)
    assert unmatched.pool(None) == (
        SplitTrade(Decimal(6), Trade(6, 100)),
    )
    assert matched.pool(None) == ()

    # Buy 6 @ 106
    pnl = pnl_book.add_trade(apple, tech, Trade(6, 106), None)
    assert pnl.strip(apple, 106) == (12, 103, 106, 0, 36000)
    _, unmatched, matched = pnl_book.get(apple, tech, None)
    assert unmatched.pool(None) == (
        SplitTrade(Decimal(6), Trade(6, 100)),
        SplitTrade(Decimal(6), Trade(6, 106)),
    )
    assert matched.pool(None) == ()

    # Buy 6 @ 103
    pnl = pnl_book.add_trade(apple, tech, Trade(6, 103), None)
    assert pnl.strip(apple, 103) == (18, 103, 103, 0, 0)
    _, unmatched, matched = pnl_book.get(apple, tech, None)
    assert unmatched.pool(None) == (
        SplitTrade(Decimal(6), Trade(6, 100)),
        SplitTrade(Decimal(6), Trade(6, 106)),
        SplitTrade(Decimal(6), Trade(6, 103)),
    )
    assert matched.pool(None) == ()

    # Sell 9 @ 105
    pnl = pnl_book.add_trade(apple, tech, Trade(-9, 105), None)
    assert pnl.strip(apple, 105) == (9, 104, 105, 27000, 9000)
    _, unmatched, matched = pnl_book.get(apple, tech, None)
    assert unmatched.pool(None) == (
        SplitTrade(Decimal(3), Trade(6, 106)),
        SplitTrade(Decimal(6), Trade(6, 103)),
    )
    assert matched.pool(None) == (
        (Decimal(-6), Trade(6, 100), Trade(-9, 105)),
        (Decimal(-3), Trade(6, 106), Trade(-9, 105)),
    )

    # Sell 9 @ 107
    pnl = pnl_book.add_trade(apple, tech, Trade(-9, 107), None)
    assert pnl.strip(apple, 107) == (0, 0, 107, 54000, 0)
    _, unmatched, matched = pnl_book.get(apple, tech, None)
    assert unmatched.pool(None) == ()
    assert matched.pool(None) == (
        (Decimal(-6), Trade(6, 100), Trade(-9, 105)),
        (Decimal(-3), Trade(6, 106), Trade(-9, 105)),
        (Decimal(-3), Trade(6, 106), Trade(-9, 107)),
        (Decimal(-6), Trade(6, 103), Trade(-9, 107))
    )
