# jetblack-pnl

Some experiments in calculating trading P&L.

## Simple Example

```python
from jetblack_pnl.core.example import SimplePnl

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
```

## Overview

A position consists of a number of buy or sell trades. When the
position becomes flat (the quantity of buys equals the quantity of sells) there is
an unambiguous result for the P&L (the amount spent minus the amount received).
Up until this point the P&L depends on the accounting method.

A obvious approach is to keep track of the average cost. Each trade is consolidated
into a single trade where the price is the average cost. This is usually *not*
what is done! In the investment world "opening" trades are matched against
the "closing" trades.

Typically, accountants prefer a FIFO (first in, first out) style of matching.
So if there were a bunch of buys and then a sell, the sell would be matched first
with the earliest buy, and then the more recent trades, until the sell quantity
matched the buys.

FIFO is used by convention. It's origin may be in standard accounting, where old
stock would likely have been cheaper to acquire, and matching new sales against old
purchases ensured the P&L was not skewed by old inventory. It is not the only
methodology however. Traders sometimes prefer a "worst price" approach, were a
sell is matched against the highest price buy.

Regardless of the approach the P&L can be characterized by the following
properties:

* quantity - how much of the asset is held.
* cost - how much has it cost to accrue the asset.
* realized - how much profit (or loss) was realized by selling from a long
  position, or buying from a short.
* unmatched - trades which have not yet been completely matched.

If the new trade extends the position (a buy from a long or flat position or a
sell from a flat or short position) the quantity increases by that of the trade
and also the cost.

If the trade reduces the position a matching trade must be found. Taking FIFO
as the method, the oldest trade is taken. There are three possibilities: The
matching trade might be exactly the same quantity (but of opposite sign), the
trade might have the larger quantity, or the match might have the larger quantity.
Where the quantities don't match exactly there must be a split. If the match
quantity is greater, the match is split and the spare is returned to the unmatched.
If the trade is larger it is split and the remainder becomes the next trade to
match.
