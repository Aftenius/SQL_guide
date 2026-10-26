"""Grade one SQL statement by the rows it returns."""

from collections.abc import Sequence
from dataclasses import dataclass

from sql_guide.domain.errors import SandboxQueryFailed
from sql_guide.domain.sandbox import (
    QueryResult,
    SqlSandbox,
    accept_learner_sql,
    accept_setup_sql,
    results_match,
)


@dataclass(frozen=True, slots=True)
class GradeSqlCommand:
    """One exercise attempt.

    Attributes:
        setup: Trusted statements that build the exercise tables.
        submission: SQL typed by the learner.
        expected_rows: Rows a correct statement returns.
        expected_columns: Column names a correct statement returns.
        ordered: Whether row order is part of the answer.
    """

    setup: tuple[str, ...]
    submission: str
    expected_rows: tuple[tuple[object, ...], ...]
    expected_columns: tuple[str, ...] | None = None
    ordered: bool = True


@dataclass(frozen=True, slots=True)
class SqlGrade:
    """Outcome of comparing a submission with the expected result.

    Attributes:
        passed: Whether the rows match.
        columns: Columns returned by the statement.
        rows: Rows returned by the statement.
        message: Short explanation safe to show the learner.
    """

    passed: bool
    columns: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]
    message: str


class GradeSql:
    """Check the sandbox policy, run the statement, and compare rows."""

    def __init__(self, sandbox: SqlSandbox) -> None:
        """Store the sandbox that executes accepted statements.

        Args:
            sandbox: Isolated executor. It never sees a rejected statement.
        """
        self._sandbox = sandbox

    async def execute(self, command: GradeSqlCommand) -> SqlGrade:
        """Grade one submission.

        Args:
            command: Setup, submission, and expected rows.

        Returns:
            The comparison. A rejected statement does not reach the sandbox.

        Raises:
            UnsafeSql: The submission or setup is outside the sandbox policy.
        """
        statement = accept_learner_sql(command.submission)
        for item in command.setup:
            accept_setup_sql(item)
        try:
            actual = await self._sandbox.execute(command.setup, statement)
        except SandboxQueryFailed as exc:
            return SqlGrade(False, (), (), str(exc))
        return _grade(command, actual)


def _grade(command: GradeSqlCommand, actual: QueryResult) -> SqlGrade:
    passed = results_match(
        actual,
        command.expected_rows,
        expected_columns=command.expected_columns,
        ordered=command.ordered,
    )
    message = "Correct" if passed else "The result does not match"
    return SqlGrade(passed, actual.columns, actual.rows, message)


def expected_rows(rows: Sequence[Sequence[object]]) -> tuple[tuple[object, ...], ...]:
    """Copy exercise rows into the immutable shape the grader stores.

    Args:
        rows: Rows from a lesson definition.

    Returns:
        Rows that cannot be mutated by the caller.
    """
    return tuple(tuple(row) for row in rows)
