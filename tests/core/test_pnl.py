"""Tests for order P&L"""

from decimal import Decimal

from jetblack_pnl.core import TradingPnl, SplitTrade, add_trade
from jetblack_pnl.impl.simple import (
    Security,
    Trade,
    MatchedPool,
    UnmatchedPool,
)


def test_long_to_short_with_splits_best_price():
    """long to short, splits, best price"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.BestPrice()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    assert pnl.quantity == 0
    assert pnl.cost == 0
    assert pnl.realized == 0

    # Buy 6 @ 100
    pnl = add_trade(pnl, Trade(6, 100), sec, unmatched, matched)
    assert pnl.quantity == 6
    assert pnl.cost == -600
    assert pnl.realized == 0

    # Buy 6 @ 106
    pnl = add_trade(pnl, Trade(6, 106), sec, unmatched, matched)
    assert pnl.quantity == 12
    assert pnl.cost == -1236
    assert pnl.realized == 0

    # Buy 6 @ 103
    pnl = add_trade(pnl, Trade(6, 103), sec, unmatched, matched)
    assert pnl.quantity == 18
    assert pnl.cost == -1854
    assert pnl.realized == 0

    # Sell 9 @ 105
    pnl = add_trade(pnl, Trade(-9, 105), sec, unmatched, matched)
    assert pnl.quantity == 9
    assert pnl.cost == -945
    assert pnl.realized == 36

    # Sell 9 @ 107
    pnl = add_trade(pnl, Trade(-9, 107), sec, unmatched, matched)
    assert pnl.quantity == 0
    assert pnl.cost == 0
    assert pnl.realized == 54


def test_long_to_short_with_splits_worst_price():
    """long to short, splits, worst price"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.WorstPrice()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    # Buy 6 at 100
    pnl = add_trade(pnl, Trade(6, 100), sec, unmatched, matched)
    assert pnl.quantity == 6
    assert pnl.cost == -600
    assert pnl.realized == 0

    # Buy 6 @ 106
    pnl = add_trade(pnl, Trade(6, 106), sec, unmatched, matched)
    assert pnl.quantity == 12
    assert pnl.cost == -1236
    assert pnl.realized == 0

    # Buy 6 @ 103
    pnl = add_trade(pnl, Trade(6, 103), sec, unmatched, matched)
    assert pnl.quantity == 18
    assert pnl.cost == -1854
    assert pnl.realized == 0

    # Sell 9 @ 105
    pnl = add_trade(pnl, Trade(-9, 105), sec, unmatched, matched)
    assert pnl.quantity == 9
    assert pnl.cost == -909
    assert pnl.realized == 0


def test_long_to_short_with_splits_fifo():
    """long to short, splits, fifo"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    # Buy 6 @ 100
    pnl = add_trade(pnl, Trade(6, 100), sec, unmatched, matched)
    assert pnl.quantity == 6
    assert pnl.cost == -600
    assert pnl.realized == 0

    # Buy 6 @ 106
    pnl = add_trade(pnl, Trade(6, 106), sec, unmatched, matched)
    assert pnl.quantity == 12
    assert pnl.cost == -1236
    assert pnl.realized == 0

    # Buy 6 @ 103
    pnl = add_trade(pnl, Trade(6, 103), sec, unmatched, matched)
    assert pnl.quantity == 18
    assert pnl.cost == -1854
    assert pnl.realized == 0

    # Sell 9 @ 105
    pnl = add_trade(pnl, Trade(-9, 105), sec, unmatched, matched)
    assert pnl.quantity == 9
    assert pnl.cost == -936
    assert pnl.realized == 27


def test_long_to_short_with_splits_lifo():
    """long to short, splits, fifo"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Lifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    # Buy 6 @ 100
    pnl = add_trade(pnl, Trade(6, 100), sec, unmatched, matched)
    assert pnl.quantity == 6
    assert pnl.cost == -600
    assert pnl.realized == 0

    # Buy 6 @ 106
    pnl = add_trade(pnl, Trade(6, 106), sec, unmatched, matched)
    assert pnl.quantity == 12
    assert pnl.cost == -1236
    assert pnl.realized == 0

    # Buy 6 @ 103
    pnl = add_trade(pnl, Trade(6, 103), sec, unmatched, matched)
    assert pnl.quantity == 18
    assert pnl.cost == -1854
    assert pnl.realized == 0

    # Sell 9 @ 105
    pnl = add_trade(pnl, Trade(-9, 105), sec, unmatched, matched)
    assert pnl.quantity == 9
    assert pnl.cost == -918
    assert pnl.realized == 9


def test_long_to_short_fifo_with_profit():
    """Buy 1 @ 100, then sell 1 @ 102 making 2"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 102), sec, unmatched, matched)
    assert pnl.quantity == 0
    assert pnl.cost == 0
    assert pnl.realized == 2
    assert len(unmatched) == 0
    expected = MatchedPool((
        (
            SplitTrade(Decimal(1), Trade(1, 100)),
            SplitTrade(Decimal(-1), Trade(-1, 102))
        ),
    ))
    assert matched == expected


def test_short_to_long_fifo_with_profit():
    """Sell 1 @ 102, then buy back 1 @ 101 making 2"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(-1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 100), sec, unmatched, matched)
    assert pnl.quantity == 0
    assert pnl.cost == 0
    assert pnl.realized == 2
    assert len(unmatched) == 0
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(-1), Trade(-1, 102)),
            SplitTrade(Decimal(1), Trade(1, 100))
        ),
    ))


def test_long_to_short_fifo_with_loss():
    """Buy 1 @ 102, then sell 1 @ 100 loosing 2"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 100), sec, unmatched, matched)
    assert pnl.quantity == 0
    assert pnl.cost == 0
    assert pnl.realized == -2
    assert len(unmatched) == 0
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(1), Trade(1, 102)),
            SplitTrade(Decimal(-1), Trade(-1, 100))
        ),
    ))


def test_short_to_long_fifo_with_loss():
    """Sell 1 @ 100, then buy back 1 @ 102 loosing 2"""

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(-1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 102), sec, unmatched, matched)
    assert pnl.quantity == 0
    assert pnl.cost == 0
    assert pnl.realized == -2
    assert len(unmatched) == 0
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(-1), Trade(-1, 100)),
            SplitTrade(Decimal(1), Trade(1, 102))
        ),
    ))


def test_long_sell_fifo_through_flat():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(1, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-2, 102), sec, unmatched, matched)
    assert pnl.quantity == -1
    assert pnl.cost == 102
    assert pnl.realized == 1
    assert unmatched == UnmatchedPool.Fifo((
        SplitTrade(Decimal(-1), Trade(-2, 102)),
    ))
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(1), Trade(1, 101)),
            SplitTrade(Decimal(-1), Trade(-2, 102))
        ),
    ))


def test_short_buy_fifo_through_flat():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(-1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(2, 101), sec, unmatched, matched)
    assert pnl.quantity == 1
    assert pnl.cost == -101
    assert pnl.realized == 1
    assert unmatched == UnmatchedPool.Fifo((
        SplitTrade(Decimal(1), Trade(2, 101)),
    ))
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(-1), Trade(-1, 102)),
            SplitTrade(Decimal(1), Trade(2, 101))
        ),
    ))


def test_one_buy_many_sells_fifo():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(10, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-5, 102), sec, unmatched, matched)
    assert pnl.quantity == 5
    assert pnl.cost == -505
    assert pnl.realized == 5
    pnl = add_trade(pnl, Trade(-5, 104), sec, unmatched, matched)
    assert pnl.quantity == 0
    assert pnl.cost == 0
    assert pnl.realized == 20
    assert len(unmatched) == 0
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(5), Trade(10, 101)),
            SplitTrade(Decimal(-5), Trade(-5, 102))
        ),
        (
            SplitTrade(Decimal(5), Trade(10, 101)),
            SplitTrade(Decimal(-5), Trade(-5, 104))
        ),
    ))


def test_pnl():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    # Buy 10 @ 100
    pnl = add_trade(pnl, Trade(10, 100), sec, unmatched, matched)
    assert pnl.strip(sec, 100) == (10, 100, 100, 0, 0)

    # What is the P&L if the price goes to 102?
    assert pnl.strip(sec, 102) == (10, 100.0, 102, 0, 20)

    # What if we buy another 5 at 102?
    pnl = add_trade(pnl, Trade(10, 102), sec, unmatched, matched)
    assert pnl.strip(sec, 102) == (20, 101.0, 102, 0, 20)

    # What is the P&L if the price goes to 104?
    assert pnl.strip(sec, 104) == (20, 101.0, 104, 0, 60)

    # What if we sell 10 at 104?
    pnl = add_trade(pnl, Trade(-10, 104), sec, unmatched, matched)
    assert pnl.strip(sec, 104) == (10, 102.0, 104, 40, 20)

    # What if the price drops to 102?
    assert pnl.strip(sec, 102) == (10, 102.0, 102, 40, 0)

    # What if we sell 10 at 102?
    pnl = add_trade(pnl, Trade(-10, 102), sec, unmatched, matched)
    assert pnl.strip(sec, 102) == (0, 0, 102, 40, 0)


def test_many_buys_one_sell_fifo():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 104), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 103), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-5, 104), sec, unmatched, matched)
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(1), Trade(1, 100)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 102)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 101)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 104)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 103)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
    ))


def test_many_buys_one_sell_lifo():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Lifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 104), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 103), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-5, 104), sec, unmatched, matched)
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(1), Trade(1, 103)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 104)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 101)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 102)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 100)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
    ))


def test_many_buys_one_sell_best_price():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.BestPrice()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 104), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 103), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-5, 104), sec, unmatched, matched)
    assert matched == MatchedPool((
        (
            SplitTrade(Decimal(1), Trade(1, 100)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 101)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 102)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 103)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 104)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
    ))


def test_many_sells_one_buy_best_price():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.BestPrice()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(-1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 104), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 103), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(5, 104), sec, unmatched, matched)

    expected = MatchedPool((
        (
            SplitTrade(Decimal(-1), Trade(-1, 104)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 103)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 102)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 101)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 100)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
    ))

    assert matched == expected


def test_many_buys_one_sell_worst_price():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.WorstPrice()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 104), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(1, 103), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-5, 104), sec, unmatched, matched)

    expected = MatchedPool((
        (
            SplitTrade(Decimal(1), Trade(1, 104)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 103)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 102)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 101)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
        (
            SplitTrade(Decimal(1), Trade(1, 100)),
            SplitTrade(Decimal(-1), Trade(-5, 104))
        ),
    ))

    assert matched == expected


def test_many_sells_one_buy_worst_price():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.WorstPrice()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade(-1, 100), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 102), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 101), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 104), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(-1, 103), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade(5, 104), sec, unmatched, matched)

    expected = MatchedPool((
        (
            SplitTrade(Decimal(-1), Trade(-1, 100)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 101)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 102)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 103)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
        (
            SplitTrade(Decimal(-1), Trade(-1, 104)),
            SplitTrade(Decimal(1), Trade(5, 104))
        ),
    ))
    assert matched == expected


def test_fraction_quantities():

    sec = Security("aapl", 1)
    matched = MatchedPool()
    unmatched = UnmatchedPool.Fifo()
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))

    pnl = add_trade(pnl, Trade("10.17", "2.54"), sec, unmatched, matched)
    pnl = add_trade(pnl, Trade("-8.17", "2.12"), sec, unmatched, matched)
    assert pnl.quantity == 2
    pnl = add_trade(pnl, Trade("-1.5", "2.05"), sec, unmatched, matched)
    assert pnl.quantity == Decimal("0.5")
