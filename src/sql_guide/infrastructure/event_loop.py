"""Windows event-loop setup for async database drivers."""

import asyncio
import sys


def use_selector_event_loop() -> None:
    """Prefer a selector loop so psycopg can run asynchronously on Windows.

    The default Proactor loop cannot drive psycopg's async connections.
    """
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
