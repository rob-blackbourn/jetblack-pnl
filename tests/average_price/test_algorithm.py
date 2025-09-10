from decimal import Decimal

from jetblack_pnl.average_price import (
    add_trade,
    ISecurity,
    ITrade,
    TradingPnl,
)


def to_decimal(number: int | Decimal | str) -> Decimal:
    return number if isinstance(number, Decimal) else Decimal(number)


class Security(ISecurity[str]):
    """A simple implementation of a security"""

    def __init__(
            self,
            key: str,
            contract_size: int | Decimal | str,
            is_cash: bool
    ) -> None:
        self._key = key
        self._contract_size = to_decimal(contract_size)
        self._is_cash = is_cash

    @property
    def key(self) -> str:
        return self._key

    @property
    def contract_size(self) -> Decimal:
        return self._contract_size

    @property
    def is_cash(self) -> bool:
        return self._is_cash


class Trade(ITrade[str | None]):
    """A simple trade"""

    def __init__(
            self,
            quantity: Decimal | int | str,
            price: Decimal | int | str,
            key: str | None = None
    ) -> None:
        self._quantity = to_decimal(quantity)
        self._price = to_decimal(price)
        self._key = key

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def price(self) -> Decimal:
        return self._price

    @property
    def key(self) -> str | None:
        return self._key

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Trade) and
            value.quantity == self.quantity and
            value.price == self.price and
            value.key == self.key
        )

    def __str__(self) -> str:
        prefix = "" if self._key is None else f"[{self._key}]: "
        side = "buy" if self.quantity > 0 else "sell"
        return f"{prefix}{side} {abs(self.quantity)} @ {self.price}"

    def __repr__(self) -> str:
        return str(self)


def test_long_crossing_short() -> None:
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))
    sec = Security(key='AAPL', contract_size=1, is_cash=False)

    # Buy 10 @ 100
    trade = Trade(quantity=10, price=100)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == 10
    assert pnl.cost == -1000.0
    assert pnl.realized == 0.0

    # Sell 5 @ 110
    trade = Trade(quantity=-5, price=110)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == 5
    assert pnl.cost == -500.0
    assert pnl.realized == 50.0

    # Sell 10 @ 120
    trade = Trade(quantity=-10, price=120)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == -5
    assert pnl.cost == 600.0
    assert pnl.realized == 150.0

    # Buy 5 @ 130
    trade = Trade(quantity=5, price=130)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == 0
    assert pnl.cost == 0.0
    assert pnl.realized == 100.0


def test_short_crossing_long() -> None:
    pnl = TradingPnl(Decimal(0), Decimal(0), Decimal(0))
    sec = Security(key='AAPL', contract_size=1, is_cash=False)

    # Sell 10 @ 100
    trade = Trade(quantity=-10, price=100)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == -10
    assert pnl.cost == 1000.0
    assert pnl.realized == 0.0

    # Buy 5 @ 110
    trade = Trade(quantity=5, price=110)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == -5
    assert pnl.cost == 500.0
    assert pnl.realized == -50.0

    # Buy 10 @ 120
    trade = Trade(quantity=10, price=120)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == 5
    assert pnl.cost == -600.0
    assert pnl.realized == -150.0

    # Sell 5 @ 130
    trade = Trade(quantity=-5, price=130)
    pnl = add_trade(pnl, trade, sec)
    assert pnl.quantity == 0
    assert pnl.cost == 0.0
    assert pnl.realized == -100.0
