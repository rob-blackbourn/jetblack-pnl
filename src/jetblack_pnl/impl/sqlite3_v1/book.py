from sqlite3 import Connection

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

    @classmethod
    def load(cls, con: Connection, key: int) -> 'Book':
        cur = con.cursor()
        cur.execute(
            """
            SELECT
                name
            FROM
                book
            WHERE
                book_key = ?
            """,
            (key,)
        )
        row = cur.fetchone()
        if row is None:
            raise KeyError("Book not found")
        name = row
        return cls(key, name)

    @classmethod
    def load_by_name(cls, con: Connection, name: str) -> 'Book':
        cur = con.cursor()
        cur.execute(
            """
            SELECT
                book_key
            FROM
                book
            WHERE
                name = ?
            """,
            (name,)
        )
        row = cur.fetchone()
        if row is None:
            raise KeyError("Book not found")
        key = row
        return cls(key, name)

    @classmethod
    def create(cls, con: Connection, name: str) -> 'Book':
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
