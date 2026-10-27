"""Run one learner statement against a practice database."""

from dataclasses import dataclass

from sql_guide.domain.practice_data import practice_setup
from sql_guide.domain.sandbox import (
    QueryResult,
    SqlSandbox,
    accept_learner_sql,
    accept_setup_sql,
)


@dataclass(frozen=True, slots=True)
class PracticeQuery:
    """One statement to run on a named practice database.

    Attributes:
        database_id: Which practice tables to create first.
        sql: The statement typed by the learner.
    """

    database_id: str
    sql: str


class RunPracticeQuery:
    """Check the sandbox policy, build the practice tables, and run the statement."""

    def __init__(self, sandbox: SqlSandbox) -> None:
        """Store the sandbox that executes accepted statements.

        Args:
            sandbox: Isolated executor. It never sees a rejected statement.
        """
        self._sandbox = sandbox

    async def execute(self, query: PracticeQuery) -> QueryResult:
        """Run one statement and return its rows.

        Args:
            query: Practice database id and the learner statement.

        Returns:
            Columns and rows from the statement. A statement without a result
            set returns empty columns and rows.

        Raises:
            UnknownPracticeDatabase: The database id is not known.
            UnsafeSql: The statement is outside the sandbox policy.
            SandboxQueryFailed: PostgreSQL rejected the statement.
        """
        setup = practice_setup(query.database_id)
        statement = accept_learner_sql(query.sql)
        for item in setup:
            accept_setup_sql(item)
        return await self._sandbox.execute(setup, statement)
