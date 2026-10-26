"""Liveness endpoint and use case."""

from fastapi.testclient import TestClient

from sql_guide.application.health import GetHealthStatus
from sql_guide.domain.health import ServiceStatus
from sql_guide.presentation.app import create_app
from tests.support import build_test_container


def test_get_health_status_reports_ok() -> None:
    """The use case reports liveness without a database."""
    status = GetHealthStatus().execute()

    assert status.status is ServiceStatus.OK


def test_health_endpoint_returns_ok() -> None:
    """GET /health answers with the liveness payload."""
    with TestClient(create_app(build_test_container())) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
