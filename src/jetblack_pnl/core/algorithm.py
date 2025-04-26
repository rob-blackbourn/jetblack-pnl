"""The algorithm for calculating P&L

A position consists of a number of executed buy or sell trades. When the
position is flat (the quantity of buys equals the quantity of sells) there is
an unambiguous result for the p/l (the amount spent minus the amount received).
Up until this point the p/l depends on which buys are matched with which sells,
and which unmatched trades remain.

Typically, accountants prefer a FIFO (first in, first out) style of matching.
So if there has be three buys, a sell matches against the earliest buy.

Traders sometimes prefer a "worst price" approach, were a sell is matched
against the highest price buy.

Regardless of the approach the p/l can be characterized by the following
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
"""

from decimal import Decimal

from .matched_pool import IMatchedPool
from .security import ISecurity
from .split_trade import SplitTrade
from .trade import ITrade
from .trading_pnl import TradingPnl
from .unmatched_pool import IUnmatchedPool


def _extend_position[TradeT: ITrade, SecurityT: ISecurity, ContextT](
        pnl: TradingPnl,
        trd: SplitTrade[TradeT],
        sec: ISecurity[SecurityT],
        unmatched: IUnmatchedPool[TradeT, ContextT],
        context: ContextT
) -> TradingPnl:
    """Extend a position.

    This happens for:

    * A buy from a long or flat position.
    * A sell from a short or flat position.

    In this situation no P&L is generated. The position size is increased, as is
    the cost of creating the position.

    Args:
        pnl (TradingPnl): The current P/L.
        trd (SplitTrade[TradeT]): The new trade.
        sec (ISecurity[SecurityT]): The security.
        unmatched (IUnmatchedPoll[TradeT, ContextT]): The pool of unmatched trades.
        context (ContextT): Some application context.

    Returns:
        TradingPnl: The new P/L
    """
    quantity = pnl.quantity + trd.quantity
    cost = pnl.cost - trd.quantity * sec.contract_size * trd.trade.price
    unmatched.append(trd, context)

    return TradingPnl(
        quantity,
        cost,
        pnl.realized,
    )


def _find_opening_trade[TradeT: ITrade, ContextT](
        closing_trade: SplitTrade[TradeT],
        unmatched: IUnmatchedPool[TradeT, ContextT],
        context: ContextT
) -> tuple[SplitTrade[TradeT], SplitTrade[TradeT], SplitTrade[TradeT] | None]:
    # Select an opening trade.
    opening_trade = unmatched.pop(closing_trade, context)

    if abs(closing_trade.quantity) > abs(opening_trade.quantity):

        # The closing trade is larger than the opening trade.
        # Split the closing trade into two: one of the same size as the opening
        # trade, and a second with the unmatched quantity.

        matched_opening_trade = opening_trade
        matched_closing_trade = SplitTrade(
            -opening_trade.quantity,
            closing_trade.trade,
        )
        unmatched_closing_trade = SplitTrade(
            closing_trade.quantity - -opening_trade.quantity,
            closing_trade.trade,
        )

    elif abs(closing_trade.quantity) < abs(opening_trade.quantity):

        # The closing trade is smaller than the opening trade.
        # Split the opening trade into two: one of the same size as the closing
        # trade, and the second with the unmatched quantity. Return the unmatched
        # opening trade to the pool.

        matched_opening_trade = SplitTrade(
            -closing_trade.quantity,
            opening_trade.trade,
        )
        matched_closing_trade = closing_trade
        unmatched_opening_trade = SplitTrade(
            opening_trade.quantity + closing_trade.quantity,
            opening_trade.trade,
        )
        unmatched.insert(unmatched_opening_trade, context)

        # As the entire closing trade has been filled there is no unmatched.
        unmatched_closing_trade = None

    else:

        # The closing trade quantity matches the opening trade quantity exactly.
        matched_opening_trade = opening_trade
        matched_closing_trade = closing_trade
        unmatched_closing_trade = None

    return matched_closing_trade, matched_opening_trade, unmatched_closing_trade


def _match[TradeT: ITrade, SecurityT: ISecurity, ContextT](
        pnl: TradingPnl,
        closing_trade: SplitTrade[TradeT],
        sec: ISecurity[SecurityT],
        unmatched: IUnmatchedPool[TradeT, ContextT],
        matched: IMatchedPool[TradeT, ContextT],
        context: ContextT
) -> tuple[SplitTrade[TradeT] | None, TradingPnl]:
    closing_trade, opening_trade, unmatched_opening_trade = _find_opening_trade(
        closing_trade,
        unmatched,
        context
    )

    matched.append(opening_trade, closing_trade, context)

    # Note that the open will have the opposite sign to the close.
    close_value = (
        closing_trade.quantity * sec.contract_size * closing_trade.trade.price
    )
    open_cost = -(
        opening_trade.quantity * sec.contract_size * opening_trade.trade.price
    )

    pnl = TradingPnl(
        pnl.quantity - opening_trade.quantity,
        pnl.cost - open_cost,
        pnl.realized + (open_cost - close_value),
    )

    return unmatched_opening_trade, pnl


def _reduce_position[TradeT: ITrade, SecurityT: ISecurity, ContextT](
        pnl: TradingPnl,
        closing: SplitTrade[TradeT] | None,
        sec: SecurityT,
        unmatched: IUnmatchedPool[TradeT, ContextT],
        matched: IMatchedPool[TradeT, ContextT],
        context: ContextT
) -> TradingPnl:
    while closing is not None and closing.quantity != 0 and unmatched.has(closing, context):
        closing, pnl = _match(
            pnl,
            closing,
            sec,
            unmatched,
            matched,
            context
        )

    if closing is not None and closing.quantity != 0:
        pnl = _add_pnl_trade(
            pnl,
            closing,
            sec,
            unmatched,
            matched,
            context
        )

    return pnl


def _add_pnl_trade[TradeT: ITrade, SecurityT: ISecurity, ContextT](
        pnl: TradingPnl,
        trd: SplitTrade[TradeT],
        sec: SecurityT,
        unmatched: IUnmatchedPool[TradeT, ContextT],
        matched: IMatchedPool[TradeT, ContextT],
        context: ContextT
) -> TradingPnl:
    if (
        # We are flat
        pnl.quantity == 0 or
        # We are long and buying
        (pnl.quantity > 0 and trd.quantity > 0) or
        # We are short and selling.
        (pnl.quantity < 0 and trd.quantity < 0)
    ):
        return _extend_position(
            pnl,
            trd,
            sec,
            unmatched,
            context
        )
    else:
        return _reduce_position(
            pnl,
            trd,
            sec,
            unmatched,
            matched,
            context
        )


def _add_cash_trade[TradeT: ITrade](
        pnl: TradingPnl,
        trd: ITrade[TradeT],
) -> TradingPnl:
    # Cash trades are always realized.
    return TradingPnl(
        Decimal(1),
        Decimal(0),
        trd.quantity + pnl.realized
    )


def add_trade[TradeT: ITrade, SecurityT: ISecurity, ContextT](
        pnl: TradingPnl,
        trd: TradeT,
        sec: SecurityT,
        unmatched: IUnmatchedPool[TradeT, ContextT],
        matched: IMatchedPool[TradeT, ContextT],
        context: ContextT
) -> TradingPnl:
    if sec.is_cash:
        return _add_cash_trade(pnl, trd)
    else:
        return _add_pnl_trade(
            pnl,
            SplitTrade(trd.quantity, trd),
            sec,
            unmatched,
            matched,
            context
        )
