"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI

from sql_guide.infrastructure.container import AppContainer, build_container
from sql_guide.infrastructure.event_loop import use_selector_event_loop
from sql_guide.presentation.auth import create_auth_router
from sql_guide.presentation.errors import register_domain_errors
from sql_guide.presentation.schemas import HealthResponse

use_selector_event_loop()


def create_health_router(container: AppContainer) -> APIRouter:
    """Build the liveness route.

    Args:
        container: Container that provides the liveness use case.

    Returns:
        A router mounted at the application root.
    """
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Return process liveness."""
        result = container.get_health.execute()
        return HealthResponse(status=result.status.value)

    return router


def create_app(container: AppContainer | None = None) -> FastAPI:
    """Assemble the HTTP application.

    Args:
        container: Wired use cases. When omitted, production adapters are used.

    Returns:
        The configured FastAPI application.
    """
    resolved = container if container is not None else build_container()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.engine = resolved.engine
        yield
        engine = getattr(app.state, "engine", None)
        if engine is not None:
            await engine.dispose()

    app = FastAPI(title=resolved.settings.app_name, lifespan=lifespan)
    register_domain_errors(app)
    app.include_router(create_health_router(resolved))
    app.include_router(create_auth_router(resolved))
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
