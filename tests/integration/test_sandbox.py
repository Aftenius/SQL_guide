"""The sandbox grades rows and cannot keep or reach application data."""

import asyncio

import psycopg
import pytest

from sql_guide.application.grade_sql import GradeSql, GradeSqlCommand
from sql_guide.domain.errors import SandboxQueryFailed
from sql_guide.infrastructure.sandbox import (
    SANDBOX_DATABASE,
    SANDBOX_ROLE,
    PostgresSandbox,
    ensure_sandbox,
)

_ADMIN_URL = "postgresql://sql_guide:sql_guide@127.0.0.1:5433/sql_guide"
_SANDBOX_URL = f"postgresql://sql_guide:sql_guide@127.0.0.1:5433/{SANDBOX_DATABASE}"
_ROLE_URL = f"postgresql://{SANDBOX_ROLE}:{SANDBOX_ROLE}@127.0.0.1:5433/sql_guide"


@pytest.fixture(scope="module")
def sandbox() -> PostgresSandbox:
    """Prepare the sandbox database once for this module."""
    try:
        asyncio.run(ensure_sandbox(_ADMIN_URL))
    except psycopg.OperationalError as exc:
        pytest.skip(f"PostgreSQL is not available: {exc}")
    return PostgresSandbox(_SANDBOX_URL)


async def test_select_matches_the_expected_rows(sandbox: PostgresSandbox) -> None:
    grade = await GradeSql(sandbox).execute(
        GradeSqlCommand(
            (
                "CREATE TABLE nums (n int)",
                "INSERT INTO nums VALUES (1), (2)",
            ),
            "SELECT n FROM nums ORDER BY n",
            ((1,), (2,)),
            expected_columns=("n",),
        )
    )

    assert grade.passed
    assert grade.rows == ((1,), (2,))


async def test_learner_statement_runs_as_the_sandbox_role(
    sandbox: PostgresSandbox,
) -> None:
    grade = await GradeSql(sandbox).execute(
        GradeSqlCommand((), "SELECT current_user", ((SANDBOX_ROLE,),))
    )

    assert grade.passed


async def test_attempt_schema_disappears_after_grading(
    sandbox: PostgresSandbox,
) -> None:
    created = await sandbox.execute(
        ("CREATE TABLE secret (n int)", "INSERT INTO secret VALUES (7)"),
        "SELECT n FROM secret",
    )
    assert created.rows == ((7,),)

    with pytest.raises(SandboxQueryFailed):
        await sandbox.execute((), "SELECT n FROM secret")


async def test_sandbox_role_cannot_connect_to_the_application_database(
    sandbox: PostgresSandbox,
) -> None:
    del sandbox

    with pytest.raises(psycopg.OperationalError):
        connection = await psycopg.AsyncConnection.connect(_ROLE_URL)
        await connection.close()
