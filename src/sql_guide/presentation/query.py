"""Route that runs one learner statement in the sandbox."""

from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter

from sql_guide.application.run_query import PracticeQuery, TaskCheck
from sql_guide.infrastructure.container import AppContainer
from sql_guide.presentation.schemas import QueryRequest, QueryResponse

_Cell = str | int | float | bool | None


def create_query_router(container: AppContainer) -> APIRouter:
    """Build the route that executes a practice query.

    Args:
        container: Use case that runs learner SQL in the sandbox.

    Returns:
        A router mounted at the application root.
    """
    router = APIRouter()

    @router.post("/query", response_model=QueryResponse)
    async def run_query(body: QueryRequest) -> QueryResponse:
        """Execute one statement against a practice database."""
        result = await container.run_practice_query.execute(
            PracticeQuery(
                database_id=body.database,
                sql=body.sql,
                checks=tuple(
                    TaskCheck(sql=item.sql, ordered=item.ordered, probe=item.probe)
                    for item in body.checks
                ),
            )
        )
        return QueryResponse(
            columns=list(result.result.columns),
            rows=[[_cell(value) for value in row] for row in result.result.rows],
            passed=list(result.passed),
        )

    return router


def _cell(value: object) -> _Cell:
    """Turn one database value into a JSON value.

    Args:
        value: A cell returned by PostgreSQL.

    Returns:
        A JSON-safe scalar. Dates and decimals become text.
    """
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Decimal | date | datetime):
        return str(value) if isinstance(value, Decimal) else value.isoformat()
    return str(value)
