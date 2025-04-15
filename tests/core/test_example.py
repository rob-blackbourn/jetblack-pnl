"""Tests for the simple implementation"""

from jetblack_pnl.impl.simple import SimplePnl


def test_fifo() -> None:
    """Test the FIFO implementation of the SimplePnl class."""

    book = SimplePnl()

    # Buy 6 @ 100
    pnl = book.add_trade('AAPL', 6, 100, 'tech')
    # (quantity, avg_cost, price, realized, unrealized)
    assert pnl.strip(100) == (6, 100, 100, 0, 0)

    # Buy 6 @ 106
    pnl = book.add_trade('AAPL', 6, 106, 'tech')
    assert pnl.strip(106) == (12, 103, 106, 0, 36)

    # Buy 6 @ 103
    pnl = book.add_trade('AAPL', 6, 103, 'tech')
    assert pnl.strip(103) == (18, 103, 103, 0, 0)

    # Sell 9 @ 105
    pnl = book.add_trade('AAPL', -9, 105, 'tech')
    assert pnl.strip(105) == (9, 104, 105, 27, 9)

    # Sell 9 @ 107
    pnl = book.add_trade('AAPL', -9, 107, 'tech')
    assert pnl.strip(107) == (0, 0, 107, 54, 0)
