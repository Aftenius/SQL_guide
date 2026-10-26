"""FastAPI application factory."""

import uvicorn
from fastapi import APIRouter, FastAPI

from sql_guide.application.health import GetHealthStatus
from sql_guide.infrastructure.config import Settings, get_settings
from sql_guide.presentation.schemas import HealthResponse


def create_health_router(get_health: GetHealthStatus) -> APIRouter:
    """Build the liveness route.

    Args:
        get_health: Use case that reports process liveness.

    Returns:
        A router mounted at the application root.
    """
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Return process liveness."""
        result = get_health.execute()
        return HealthResponse(status=result.status.value)

    return router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Assemble the HTTP application.

    Args:
        settings: Explicit settings. When omitted, settings come from the environment.

    Returns:
        The configured FastAPI application.
    """
    resolved = settings if settings is not None else get_settings()
    app = FastAPI(title=resolved.app_name)
    app.include_router(create_health_router(GetHealthStatus()))
    return app


app = create_app()


def main() -> None:
    """Run the API for local development."""
    uvicorn.run(
        "sql_guide.presentation.app:app",
        host="127.0.0.1",
        port=8000,
        factory=False,
    )
