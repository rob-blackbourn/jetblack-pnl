from sqlite3 import Connection, Cursor
from typing import Self

from ...core import IBook


class Book(IBook[int]):

    def __init__(
            self,
            key: int,
            name: str,
    ) -> None:
        self._key = key
        self._name = name

    @property
    def key(self) -> int:
        return self._key

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self):
        return self.name

    @classmethod
    def load(cls, cur: Cursor, key: int) -> Self:
        cur.execute(
            """
            SELECT
                name
            FROM
                book
            WHERE
                book_id = ?
            """,
            (key,)
        )
        row = cur.fetchone()
        if row is None:
            raise KeyError("Book not found")
        name = row[0]
        return cls(key, name)

    @classmethod
    def create(cls, con: Connection, name: str) -> Self:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO book(name)
            VALUES (?)
            """,
            (name,)
        )
        key = cur.lastrowid
        assert key is not None
        return cls(key, name)
