from decimal import Decimal

from .security import ISecurity
from .trade import ITrade
from .trading_pnl import TradingPnl


def _extend_position[TradeT: ITrade, SecurityT: ISecurity](
        pnl: TradingPnl,
        trd: TradeT,
        sec: SecurityT,
) -> TradingPnl:
    quantity = pnl.quantity + trd.quantity
    cost = pnl.cost - trd.quantity * sec.contract_size * trd.price
    return TradingPnl(
        quantity,
        cost,
        pnl.realized,
    )


def _reduce_position[TradeT: ITrade, SecurityT: ISecurity](
        pnl: TradingPnl,
        trd: TradeT,
        sec: SecurityT,
) -> TradingPnl:
    if trd.quantity > 0:
        closing_quantity = max(trd.quantity, -pnl.quantity)
    else:
        closing_quantity = max(trd.quantity, -pnl.quantity)

    close_value = (
        closing_quantity * sec.contract_size * trd.price
    )
    open_cost = -(
        closing_quantity * sec.contract_size * (pnl.cost / pnl.quantity)
    )

    pnl = TradingPnl(
        pnl.quantity + closing_quantity,
        pnl.cost - open_cost,
        pnl.realized + (open_cost - close_value),
    )

    if closing_quantity != trd.quantity:
        remaining_quantity = trd.quantity - closing_quantity
        cost = pnl.cost - remaining_quantity * sec.contract_size * trd.price
        pnl = TradingPnl(
            remaining_quantity,
            cost,
            pnl.realized,
        )

    return pnl


def _add_pnl_trade[TradeT: ITrade, SecurityT: ISecurity](
        pnl: TradingPnl,
        trd: TradeT,
        sec: SecurityT,
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
        )
    else:
        return _reduce_position(
            pnl,
            trd,
            sec,
        )


def _add_cash_trade[TradeT: ITrade](
        pnl: TradingPnl,
        trd: TradeT,
) -> TradingPnl:
    # Cash trades are always realized.
    return TradingPnl(
        Decimal(0),
        Decimal(0),
        trd.quantity + pnl.realized
    )


def add_trade[TradeT: ITrade, SecurityT: ISecurity](
        pnl: TradingPnl,
        trd: TradeT,
        sec: SecurityT,
) -> TradingPnl:
    if sec.is_cash:
        return _add_cash_trade(pnl, trd)
    else:
        return _add_pnl_trade(
            pnl,
            trd,
            sec,
        )
