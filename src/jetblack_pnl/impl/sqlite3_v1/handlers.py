"""SQLite example"""

from datetime import datetime
from decimal import Decimal
import sqlite3


def adapt_decimal(value: Decimal) -> str:
    text = str(value)
    return text


def convert_decimal(buf: bytes) -> Decimal:
    text = buf.decode('ascii')
    value = Decimal(text)
    return value


def adapt_datetime(val: datetime) -> str:
    return val.isoformat()


def convert_datetime(val: bytes) -> datetime:
    return datetime.fromisoformat(val.decode())


def register_handlers() -> None:
    # Add decimal support
    sqlite3.register_adapter(Decimal, adapt_decimal)
    sqlite3.register_converter("DECIMAL", convert_decimal)

    # Add datetime support
    sqlite3.register_adapter(datetime, adapt_datetime)
    sqlite3.register_converter("DATETIME", convert_datetime)
