"""Practice queries use trusted setup and stop before an unsafe statement."""

from collections.abc import Sequence

import pytest
from fastapi.testclient import TestClient

from sql_guide.application.run_query import PracticeQuery, RunPracticeQuery
from sql_guide.domain.errors import UnknownPracticeDatabase, UnsafeSql
from sql_guide.domain.practice_data import practice_setup
from sql_guide.domain.sandbox import QueryResult, accept_setup_sql
from sql_guide.presentation.app import create_app
from tests.support import build_test_container


class RecordingSandbox:
    """Sandbox double that records the setup it was given."""

    def __init__(self) -> None:
        self.setup: tuple[str, ...] = ()
        self.statement = ""

    async def execute(self, setup: Sequence[str], statement: str) -> QueryResult:
        """Remember the call and return one title."""
        self.setup = tuple(setup)
        self.statement = statement
        return QueryResult(("title",), (("Север",), ("Юг",), ("Восток",)))


def test_shop_setup_is_a_list_of_single_statements() -> None:
    setup = practice_setup("shop")
    assert any("CREATE TABLE books" in item for item in setup)
    assert any("NULL" in item and "Омск" in item for item in setup)
    for item in setup:
        accept_setup_sql(item)


def test_unknown_database_is_rejected() -> None:
    with pytest.raises(UnknownPracticeDatabase):
        practice_setup("other")


async def test_select_reaches_the_sandbox_with_shop_tables() -> None:
    sandbox = RecordingSandbox()
    result = await RunPracticeQuery(sandbox).execute(
        PracticeQuery("shop", "SELECT title FROM books")
    )

    assert result.rows == (("Север",), ("Юг",), ("Восток",))
    assert sandbox.statement == "SELECT title FROM books"
    assert any("CREATE TABLE books" in item for item in sandbox.setup)


async def test_two_statements_never_reach_the_sandbox() -> None:
    sandbox = RecordingSandbox()

    with pytest.raises(UnsafeSql):
        await RunPracticeQuery(sandbox).execute(
            PracticeQuery("shop", "SELECT 1; DROP TABLE books")
        )

    assert sandbox.statement == ""


def test_query_route_returns_rows() -> None:
    container = build_test_container()
    container.run_practice_query = RunPracticeQuery(RecordingSandbox())
    with TestClient(create_app(container)) as client:
        response = client.post(
            "/query",
            json={"database": "shop", "sql": "SELECT title FROM books"},
        )

    assert response.status_code == 200
    assert response.json()["columns"] == ["title"]
    assert response.json()["rows"][0] == ["Север"]
