"""FastAPI application factory."""

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sql_guide.infrastructure.container import AppContainer, build_container
from sql_guide.infrastructure.event_loop import use_selector_event_loop
from sql_guide.presentation.auth import create_auth_router
from sql_guide.presentation.errors import register_domain_errors
from sql_guide.presentation.learner_model import create_learner_model_router
from sql_guide.presentation.practice import create_practice_router
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_frontend_origins(resolved.settings.frontend_origin),
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    register_domain_errors(app)
    app.include_router(create_health_router(resolved))
    app.include_router(create_auth_router(resolved))
    app.include_router(create_practice_router(resolved))
    app.include_router(create_learner_model_router(resolved))
    return app


def _frontend_origins(origin: str) -> list[str]:
    """Allow the configured UI origin and its localhost alias."""
    origins = [origin]
    if "127.0.0.1" in origin:
        origins.append(origin.replace("127.0.0.1", "localhost"))
    return origins


app = create_app()


def main() -> None:
    """Run the API for local development.

    Uvicorn's default Windows loop is Proactor, which psycopg cannot use.
    """
    use_selector_event_loop()
    config = uvicorn.Config(
        "sql_guide.presentation.app:app",
        host="127.0.0.1",
        port=8000,
    )
    server = uvicorn.Server(config)
    factory = asyncio.SelectorEventLoop if sys.platform == "win32" else None
    asyncio.run(server.serve(), loop_factory=factory)
