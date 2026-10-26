"""Learner SQL is accepted or rejected before it can reach PostgreSQL."""

from collections.abc import Sequence

import pytest

from sql_guide.application.grade_sql import GradeSql, GradeSqlCommand
from sql_guide.domain.errors import UnsafeSql
from sql_guide.domain.sandbox import QueryResult, accept_learner_sql, results_match


class RecordingSandbox:
    """Sandbox double that records whether grading executed SQL."""

    def __init__(self, result: QueryResult) -> None:
        self.calls = 0
        self._result = result

    async def execute(self, setup: Sequence[str], statement: str) -> QueryResult:
        """Return the prepared result and count the call."""
        del setup, statement
        self.calls += 1
        return self._result


def test_one_select_is_accepted() -> None:
    sql = "  WITH rows AS (SELECT 1 AS n) SELECT n FROM rows  "
    assert accept_learner_sql(sql) == sql.strip()


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1; SELECT 2",
        "SELECT 1;;",
        "COPY secret TO STDOUT",
        "SET ROLE sql_guide",
        "DO $$ BEGIN END $$",
        "SELECT set_config('role', 'sql_guide', true)",
        "SELECT pg_read_file('/etc/passwd')",
        "SELECT pg_catalog.pg_read_file('/etc/passwd')",
        "SELECT \"set_config\"('role', 'sql_guide', true)",
        "GRANT USAGE ON SCHEMA public TO PUBLIC",
        "",
    ],
)
def test_dangerous_scripts_are_rejected(sql: str) -> None:
    with pytest.raises(UnsafeSql):
        accept_learner_sql(sql)


def test_semicolon_inside_a_string_or_dollar_quote_stays_one_statement() -> None:
    accept_learner_sql("SELECT ';'")
    accept_learner_sql("SELECT $body$;$body$")
    accept_learner_sql("-- SET ROLE\nSELECT 1")


def test_comment_hides_a_second_statement() -> None:
    accept_learner_sql("SELECT 1 /* ; DROP TABLE users */")


async def test_rejected_sql_never_reaches_the_sandbox() -> None:
    sandbox = RecordingSandbox(QueryResult(("n",), ((1,),)))
    grader = GradeSql(sandbox)

    with pytest.raises(UnsafeSql):
        await grader.execute(
            GradeSqlCommand((), "SELECT 1; SET ROLE sql_guide", ((1,),))
        )

    assert sandbox.calls == 0


async def test_grade_compares_rows_and_ignores_order_when_asked() -> None:
    sandbox = RecordingSandbox(QueryResult(("n",), ((2,), (1,))))
    grader = GradeSql(sandbox)
    command = GradeSqlCommand(
        ("CREATE TABLE nums (n int)",),
        "SELECT n FROM nums",
        ((1,), (2,)),
        expected_columns=("n",),
        ordered=False,
    )

    grade = await grader.execute(command)

    assert grade.passed
    assert sandbox.calls == 1
    assert results_match(QueryResult(("n",), ((2,), (1,))), ((1,), (2,)), ordered=False)
    assert not results_match(QueryResult(("n",), ((2,), (1,))), ((1,), (2,)))
