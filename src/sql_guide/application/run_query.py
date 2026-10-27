"""Run one learner statement against a practice database."""

from dataclasses import dataclass

from sql_guide.domain.errors import SandboxQueryFailed, UnsafeSql
from sql_guide.domain.practice_data import practice_setup
from sql_guide.domain.sandbox import (
    QueryResult,
    SqlSandbox,
    accept_learner_sql,
    accept_setup_sql,
    results_match,
)

_MAX_CHECKS = 8


@dataclass(frozen=True, slots=True)
class TaskCheck:
    """One hidden solution used only to decide if a task is done.

    Attributes:
        sql: Statement that produces the task's result.
        ordered: Whether row order is part of the answer.
        probe: Statement read after ``sql`` when the task changes rows.
    """

    sql: str
    ordered: bool = False
    probe: str = ""


@dataclass(frozen=True, slots=True)
class PracticeQuery:
    """One statement to run on a named practice database.

    Attributes:
        database_id: Which practice tables to create first.
        sql: The statement typed by the learner.
        checks: Solutions aligned with the tasks on the page. Blank sql is skipped.
    """

    database_id: str
    sql: str
    checks: tuple[TaskCheck, ...] = ()


@dataclass(frozen=True, slots=True)
class PracticeRun:
    """Rows to show and the task indexes the statement solved.

    Attributes:
        result: Columns and rows from the learner statement.
        passed: Indexes into ``checks`` whose solution matches.
    """

    result: QueryResult
    passed: tuple[int, ...]


class RunPracticeQuery:
    """Check the sandbox policy, build the practice tables, and run the statement."""

    def __init__(self, sandbox: SqlSandbox) -> None:
        """Store the sandbox that executes accepted statements.

        Args:
            sandbox: Isolated executor. It never sees a rejected statement.
        """
        self._sandbox = sandbox

    async def execute(self, query: PracticeQuery) -> PracticeRun:
        """Run one statement and compare it with the lesson's solutions.

        Args:
            query: Practice database id, the learner statement, and task solutions.

        Returns:
            The learner rows and the indexes of tasks those rows solve.

        Raises:
            UnknownPracticeDatabase: The database id is not known.
            UnsafeSql: The learner statement is outside the sandbox policy.
            SandboxQueryFailed: PostgreSQL rejected the learner statement.
        """
        setup = practice_setup(query.database_id)
        statement = accept_learner_sql(query.sql)
        for item in setup:
            accept_setup_sql(item)
        actual = await self._sandbox.execute(setup, statement)
        passed = await self._passed(
            setup, statement, actual, query.checks[:_MAX_CHECKS]
        )
        return PracticeRun(actual, passed)

    async def _passed(
        self,
        setup: tuple[str, ...],
        statement: str,
        actual: QueryResult,
        checks: tuple[TaskCheck, ...],
    ) -> tuple[int, ...]:
        solved: list[int] = []
        for index, check in enumerate(checks):
            if check.sql.strip() == "":
                continue
            try:
                if await self._matches(setup, statement, actual, check):
                    solved.append(index)
            except (UnsafeSql, SandboxQueryFailed):
                continue
        return tuple(solved)

    async def _matches(
        self,
        setup: tuple[str, ...],
        statement: str,
        actual: QueryResult,
        check: TaskCheck,
    ) -> bool:
        solution = accept_learner_sql(check.sql)
        probe = accept_learner_sql(check.probe) if check.probe.strip() else None
        if probe is None:
            expected = await self._sandbox.execute(setup, solution)
            got = actual
        else:
            got = await self._sandbox.execute(setup, statement, probe=probe)
            expected = await self._sandbox.execute(setup, solution, probe=probe)
        return results_match(
            got,
            expected.rows,
            expected_columns=expected.columns,
            ordered=check.ordered,
        )
