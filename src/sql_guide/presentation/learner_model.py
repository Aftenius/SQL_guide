"""Profile routes for the learner's model key."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sql_guide.application.learner_model import (
    CheckLearnerModelCommand,
    SaveLearnerModelCommand,
)
from sql_guide.domain.user import UserId
from sql_guide.infrastructure.container import AppContainer
from sql_guide.presentation.schemas import (
    CheckLearnerModelRequest,
    LearnerModelResponse,
    SaveLearnerModelRequest,
)

_bearer = HTTPBearer(auto_error=False)


def create_learner_model_router(container: AppContainer) -> APIRouter:
    """Build the profile routes that store a model key.

    Args:
        container: Use cases that save, read, and check the key.

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

    @router.get(
        "/me/model",
        response_model=LearnerModelResponse,
        response_model_exclude_none=True,
    )
    async def describe_model(
        user_id: Annotated[UserId, Depends(current_user_id)],
    ) -> LearnerModelResponse:
        """Return the saved model without its key."""
        described = await container.describe_learner_model.execute(user_id)
        if described is None:
            return LearnerModelResponse(configured=False)
        return LearnerModelResponse(
            configured=True,
            provider=described.provider,
            model=described.model,
            hint=described.hint,
            updated_at=described.updated_at,
        )

    @router.put(
        "/me/model",
        response_model=LearnerModelResponse,
        response_model_exclude_none=True,
    )
    async def save_model(
        body: SaveLearnerModelRequest,
        user_id: Annotated[UserId, Depends(current_user_id)],
    ) -> LearnerModelResponse:
        """Encrypt and store the model key."""
        described = await container.save_learner_model.execute(
            SaveLearnerModelCommand(
                user_id=user_id,
                provider=body.provider,
                model=body.model,
                api_key=body.api_key,
            )
        )
        return LearnerModelResponse(
            configured=True,
            provider=described.provider,
            model=described.model,
            hint=described.hint,
            updated_at=described.updated_at,
        )

    @router.delete("/me/model", status_code=204)
    async def clear_model(
        user_id: Annotated[UserId, Depends(current_user_id)],
    ) -> Response:
        """Remove the saved model key."""
        await container.clear_learner_model.execute(user_id)
        return Response(status_code=204)

    @router.post("/me/model/check", status_code=204)
    async def check_model(
        body: CheckLearnerModelRequest,
        user_id: Annotated[UserId, Depends(current_user_id)],
    ) -> Response:
        """Ask the provider whether the key is accepted."""
        await container.check_learner_model.execute(
            CheckLearnerModelCommand(
                user_id=user_id,
                provider=body.provider,
                model=body.model,
                api_key=body.api_key,
            )
        )
        return Response(status_code=204)

    return router
