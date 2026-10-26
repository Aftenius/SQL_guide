"""Practice calendar routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sql_guide.application.practice import RecordSolveCommand
from sql_guide.domain.user import UserId
from sql_guide.infrastructure.container import AppContainer
from sql_guide.presentation.schemas import (
    PracticeCalendarResponse,
    ReviewResponse,
    SolvedDayResponse,
    SolveRequest,
    SolveResponse,
)

_bearer = HTTPBearer(auto_error=False)


def create_practice_router(container: AppContainer) -> APIRouter:
    """Build the calendar and solve routes.

    Args:
        container: Use cases that record and read practice.

    Returns:
        A router mounted at the application root.
    """
    router = APIRouter()

    async def current_user_id(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    ) -> UserId:
        """Read the account id from the bearer token."""
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        learner = await container.get_current_learner.execute(credentials.credentials)
        return UserId(learner.id)

    @router.get("/me/practice", response_model=PracticeCalendarResponse)
    async def practice_calendar(
        user_id: Annotated[UserId, Depends(current_user_id)],
    ) -> PracticeCalendarResponse:
        """Return solved days and scheduled reviews."""
        overview = await container.get_practice_calendar.execute(user_id)
        return PracticeCalendarResponse(
            today=overview.today,
            streak=overview.streak,
            days=[
                SolvedDayResponse(date=day.on, solved=day.solved)
                for day in overview.solved_days
            ],
            reviews=[
                ReviewResponse(
                    track=card.track,
                    lesson=card.lesson,
                    due_on=card.due_on,
                    interval_days=card.interval_days,
                )
                for card in overview.reviews
            ],
        )

    @router.post("/me/practice", response_model=SolveResponse)
    async def record_solve(
        body: SolveRequest,
        user_id: Annotated[UserId, Depends(current_user_id)],
    ) -> SolveResponse:
        """Count a solved step and schedule the next review."""
        result = await container.record_solve.execute(
            RecordSolveCommand(user_id=user_id, track=body.track, lesson=body.lesson)
        )
        return SolveResponse(
            track=result.card.track,
            lesson=result.card.lesson,
            due_on=result.card.due_on,
            interval_days=result.card.interval_days,
            counted=result.counted,
            today=result.today,
        )

    return router
