"""A simple security"""

from decimal import Decimal

from sqlite3 import Cursor, Connection

from ...core import ISecurity

from .utils import to_decimal, AnyNumber


class Security(ISecurity[int]):
    """A security with an integer id"""

    def __init__(
            self,
            key: int,
            name: str,
            contract_size: AnyNumber,
            is_cash: bool,
            ccy: str
    ) -> None:
        self._key = key
        self._name = name
        self._contract_size = to_decimal(contract_size)
        self._is_cash = is_cash
        self._ccy = ccy

    @property
    def key(self) -> int:
        return self._key

    @property
    def name(self) -> str:
        return self._name

    @property
    def contract_size(self) -> Decimal:
        return self._contract_size

    @property
    def is_cash(self) -> bool:
        return self._is_cash

    @property
    def ccy(self) -> str:
        return self._ccy

    def __repr__(self):
        return self.name

    @classmethod
    def load(cls, cur: Cursor, key: int) -> 'Security':
        cur.execute(
            """
            SELECT
                name,
                contract_size,
                is_cash,
                ccy
            FROM
                security
            WHERE
                security_id = ?
            """,
            (key,)
        )
        row = cur.fetchone()
        if row is None:
            raise KeyError("Security not found")
        name, contract_size, is_cash, ccy = row
        return cls(key, name, contract_size, is_cash, ccy)

    @classmethod
    def create(
            cls,
            con: Connection,
            name: str,
            contract_size: AnyNumber,
            is_cash: bool,
            ccy: str
    ) -> 'Security':
        cur = con.cursor()
        contract_size = to_decimal(contract_size)
        cur.execute(
            """
            INSERT INTO security(name, contract_size, is_cash, ccy)
            VALUES (?, ?, ?, ?)
            """,
            (name, contract_size, is_cash, ccy)
        )
        key = cur.lastrowid
        assert key is not None
        return cls(key, name, contract_size, is_cash, ccy)
