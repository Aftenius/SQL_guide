"""Liveness endpoint and use case."""

from fastapi.testclient import TestClient

from sql_guide.application.health import GetHealthStatus
from sql_guide.domain.health import ServiceStatus
from sql_guide.infrastructure.config import Settings
from sql_guide.presentation.app import create_app


def test_get_health_status_reports_ok() -> None:
    """The use case reports liveness without a database."""
    status = GetHealthStatus().execute()

    assert status.status is ServiceStatus.OK


def test_health_endpoint_returns_ok() -> None:
    """GET /health answers with the liveness payload."""
    settings = Settings(app_name="SQL Guide Test", database_url="postgresql://unused")
    client = TestClient(create_app(settings))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
