"""The context is arbitrary data that is passed to the pnl operations.

It may be useful for things such as database sessions.
"""

from typing import TypeVar

TContext = TypeVar('TContext')
