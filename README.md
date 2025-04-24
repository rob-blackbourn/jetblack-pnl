# jetblack-pnl

Some experiments in calculating trading P&L using Python 3.12.

## Simple Example

```python
from jetblack_pnl.impl.simple import Security, Book, SimplePnlBook

pnl_book = SimplePnlBook()
tech = Book('tech')
apple = Security('AAPL', 1000, False)

# Buy 6 @ 100
pnl = pnl_book.add(apple, tech, 6, 100)
# (quantity, avg_cost, price, realized, unrealized)
assert pnl.strip(apple, 100) == (6, 100, 100, 0, 0)

# Buy 6 @ 106
pnl = pnl_book.add(apple, tech, 6, 106)
assert pnl.strip(apple, 106) == (12, 103, 106, 0, 36000)

# Buy 6 @ 103
pnl = pnl_book.add(apple, tech, 6, 103)
assert pnl.strip(apple, 103) == (18, 103, 103, 0, 0)

# Sell 9 @ 105
pnl = pnl_book.add(apple, tech, -9, 105)
assert pnl.strip(apple, 105) == (9, 104, 105, 27000, 9000)

# Sell 9 @ 107
pnl = pnl_book.add(apple, tech, -9, 107)
assert pnl.strip(apple, 107) == (0, 0, 107, 54000, 0)
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
sell is matched against the highest buy price.

Regardless of the approach the P&L can be characterized by the following
properties:

* quantity - how much of the asset is held.
* cost - how much has it cost to accrue the asset.
* realized - how much profit (or loss) was realized by selling from a long
  position, or buying from a short.
* unmatched - trades which have not yet been completely matched.

If the new trade extends the position (a buy from a long or flat position or a
sell from a flat or short position) the quantity increases by that of the trade
and also the cost. This will be called an *opening* trade.

If the trade reduces the position (a *closing* trade) a matching trade must be
found. Taking FIFO as the method, the oldest trade is taken. There are three
possibilities: The matching trade might be exactly the same quantity (but of opposite sign), the
trade might have the larger quantity, or the match might have the larger quantity.
Where the quantities don't match exactly there must be a split. If the match
quantity is greater, the match is split and the spare is returned to the unmatched.
If the trade is larger it is split and the remainder becomes the next trade to
match.

## Code

The code is split into two parts, `core`, and `impl` (implementations). The core
part contains the types and the algorithms, while the implementations provide some
examples of how to use the core code.

### Core Code

The folder `src/jetblack_pnl/core` contains the types and algorithms to calculate
P&L. The file `algorithm.py` contains the key code.

### Implementations

There are a number of implementations.

#### Simple Implementation

The `src/jetblack_pnl/impl/simple` folder contains a trivial in-memory
implementation with code for 4 matching methods (FIFO, LIFO, best price, worst
price).

This is largely used for testing and demonstrating the algorithm.

#### Sqlite Implementation

There are some folders which contain implementations which persist positions
to a sqlite database, to demonstrate how this might be done in a production
system.
