"""Sandbox policy and result comparison. No database driver lives here."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from sql_guide.domain.errors import UnsafeSql

_LEARNER_START = frozenset(
    {
        "select",
        "with",
        "insert",
        "update",
        "delete",
        "values",
        "create",
        "alter",
        "drop",
    }
)
_SETUP_START = _LEARNER_START | frozenset({"create", "drop", "alter", "truncate"})
_FORBIDDEN = frozenset(
    {
        "copy",
        "dblink",
        "dblink_connect",
        "dblink_exec",
        "lo_export",
        "lo_from_bytea",
        "lo_import",
        "pg_advisory_lock",
        "pg_advisory_lock_shared",
        "pg_cancel_backend",
        "pg_promote",
        "pg_read_binary_file",
        "pg_read_file",
        "pg_reload_conf",
        "pg_ls_dir",
        "pg_rotate_logfile",
        "pg_sleep",
        "pg_stat_file",
        "pg_terminate_backend",
        "set_config",
    }
)
_MAX_SQL_LENGTH = 8_000
_MAX_ROWS = 500


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Rows returned by one learner statement.

    Attributes:
        columns: Result column names, empty when the statement returns none.
        rows: Result rows in database order.
    """

    columns: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]


class SqlSandbox(Protocol):
    """Runs trusted setup and one learner statement in an isolated schema."""

    async def execute(
        self,
        setup: Sequence[str],
        statement: str,
        *,
        probe: str | None = None,
    ) -> QueryResult:
        """Apply setup, run the statement, and discard the schema.

        Args:
            setup: Trusted statements that create the exercise data.
            statement: One learner statement already accepted by the policy.
            probe: When set, a second statement whose rows are returned instead.
                The first statement still runs, so a change can be read back.

        Returns:
            The rows the learner statement produced, or the probe rows.
        """
        ...


def accept_learner_sql(sql: str) -> str:
    """Return the learner statement when the sandbox policy accepts it.

    Args:
        sql: SQL submitted for grading.

    Returns:
        The same SQL, stripped of surrounding whitespace.

    Raises:
        UnsafeSql: The script is empty, contains several statements, or uses
            a command the sandbox does not run.
    """
    return _accept(sql, _LEARNER_START)


def accept_setup_sql(sql: str) -> str:
    """Return one trusted setup statement.

    Args:
        sql: Statement authored with the exercise, not typed by the learner.

    Returns:
        The same SQL, stripped of surrounding whitespace.

    Raises:
        UnsafeSql: The setup script is not a single allowed statement.
    """
    return _accept(sql, _SETUP_START)


def results_match(
    actual: QueryResult,
    expected_rows: Sequence[Sequence[object]],
    *,
    expected_columns: Sequence[str] | None = None,
    ordered: bool = True,
) -> bool:
    """Compare a sandbox result with the exercise's expected result.

    Args:
        actual: Rows produced by the learner statement.
        expected_rows: Rows the exercise expects.
        expected_columns: Column names to require. Omitted names are ignored.
        ordered: When false, row order does not matter.

    Returns:
        Whether the result satisfies the exercise.
    """
    if len(actual.rows) > _MAX_ROWS:
        return False
    if expected_columns is not None and tuple(expected_columns) != actual.columns:
        return False
    expected = tuple(tuple(row) for row in expected_rows)
    if ordered:
        return actual.rows == expected
    return sorted(actual.rows, key=_row_key) == sorted(expected, key=_row_key)


def _accept(sql: str, allowed_start: frozenset[str]) -> str:
    if len(sql) > _MAX_SQL_LENGTH or "\x00" in sql:
        raise UnsafeSql("This statement is not allowed")
    words = _single_statement_words(sql)
    forbidden = any(word in _FORBIDDEN for word in words)
    if not words or words[0] not in allowed_start or forbidden:
        raise UnsafeSql("This statement is not allowed")
    return sql.strip()


def _single_statement_words(sql: str) -> tuple[str, ...]:
    statements = _statements(sql)
    significant = [words for words in statements if words]
    if not significant:
        raise UnsafeSql("A statement is required")
    if len(statements) != 1:
        raise UnsafeSql("Only one statement is allowed")
    return tuple(significant[0])


def _statements(sql: str) -> list[list[str]]:
    words: list[str] = []
    closed: list[list[str]] = []
    index = 0
    length = len(sql)
    while index < length:
        step, word, boundary = _next_token(sql, index)
        index += step
        if boundary:
            closed.append(words)
            words = []
            continue
        if word is not None:
            words.append(word)
    if words:
        closed.append(words)
    return closed


def _next_token(sql: str, index: int) -> tuple[int, str | None, bool]:
    """Return characters consumed, an identifier, and whether a statement ended."""
    char = sql[index]
    if char.isspace():
        return 1, None, False
    if sql.startswith("--", index):
        newline = sql.find("\n", index)
        return (len(sql) - index if newline < 0 else newline - index + 1), None, False
    if sql.startswith("/*", index):
        return _block_comment(sql, index), None, False
    if char == "'":
        return _quoted(sql, index, "'"), None, False
    if char == '"':
        return _quoted_identifier(sql, index)
    if char == "$":
        dollar = _dollar_quote(sql, index)
        if dollar > 0:
            return dollar, None, False
    if char == ";":
        return 1, None, True
    if _is_word_char(char):
        end = index + 1
        while end < len(sql) and _is_word_char(sql[end]):
            end += 1
        return end - index, sql[index:end].lower(), False
    return 1, None, False


def _quoted(sql: str, index: int, quote: str) -> int:
    end = index + 1
    while end < len(sql):
        if sql[end] == quote:
            if end + 1 < len(sql) and sql[end + 1] == quote:
                end += 2
                continue
            return end + 1 - index
        end += 1
    raise UnsafeSql("This statement is not allowed")


def _quoted_identifier(sql: str, index: int) -> tuple[int, str, bool]:
    end = index + 1
    pieces: list[str] = []
    while end < len(sql):
        if sql[end] == '"':
            if end + 1 < len(sql) and sql[end + 1] == '"':
                pieces.append('"')
                end += 2
                continue
            return end + 1 - index, "".join(pieces).lower(), False
        pieces.append(sql[end])
        end += 1
    raise UnsafeSql("This statement is not allowed")


def _dollar_quote(sql: str, index: int) -> int:
    end = index + 1
    while end < len(sql) and (sql[end].isalnum() or sql[end] == "_"):
        end += 1
    if end >= len(sql) or sql[end] != "$":
        return 0
    tag = sql[index : end + 1]
    close = sql.find(tag, end + 1)
    if close < 0:
        raise UnsafeSql("This statement is not allowed")
    return close + len(tag) - index


def _block_comment(sql: str, index: int) -> int:
    depth = 1
    end = index + 2
    while end < len(sql) and depth > 0:
        if sql.startswith("/*", end):
            depth += 1
            end += 2
            continue
        if sql.startswith("*/", end):
            depth -= 1
            end += 2
            continue
        end += 1
    if depth != 0:
        raise UnsafeSql("This statement is not allowed")
    return end - index


def _is_word_char(char: str) -> bool:
    return char.isalnum() or char in {"_", "$"}


def _row_key(row: tuple[object, ...]) -> tuple[str, ...]:
    return tuple(repr(item) for item in row)
