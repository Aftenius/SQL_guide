"""HTTP registration and session flow."""

from fastapi.testclient import TestClient

from sql_guide.presentation.app import create_app
from tests.support import build_test_container

_PASSWORD = "password123"


def test_register_login_and_read_profile() -> None:
    """A learner can register, log in, and read the saved progress root."""
    with TestClient(create_app(build_test_container())) as client:
        created = client.post(
            "/auth/register",
            json={"email": "Ada@Example.com", "password": _PASSWORD},
        )
        logged_in = client.post(
            "/auth/login",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        me = client.get(
            "/me",
            headers={"Authorization": f"Bearer {logged_in.json()['access_token']}"},
        )

    assert created.status_code == 201
    assert created.json()["email"] == "ada@example.com"
    assert logged_in.status_code == 200
    assert "refresh_token" in logged_in.cookies
    assert me.status_code == 200
    assert me.json()["id"] == created.json()["id"]
    assert me.json()["profile_created_at"] == created.json()["profile_created_at"]


def test_register_reports_duplicate_and_weak_password() -> None:
    """Registration explains a taken email and a short password."""
    with TestClient(create_app(build_test_container())) as client:
        client.post(
            "/auth/register",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        duplicate = client.post(
            "/auth/register",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        weak = client.post(
            "/auth/register",
            json={"email": "other@example.com", "password": "short"},
        )

    assert duplicate.status_code == 409
    assert weak.status_code == 422


def test_refresh_rotates_cookie_and_logout_revokes_it() -> None:
    """The refresh cookie is replaced, then logout makes it useless."""
    with TestClient(create_app(build_test_container())) as client:
        client.post(
            "/auth/register",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        client.post(
            "/auth/login",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        first_cookie = client.cookies.get("refresh_token")
        refreshed = client.post("/auth/refresh")
        rotated_cookie = client.cookies.get("refresh_token")
        client.cookies.set("refresh_token", first_cookie)
        reused = client.post("/auth/refresh")
        client.cookies.set("refresh_token", rotated_cookie)
        logged_out = client.post("/auth/logout")
        after_logout = client.post("/auth/refresh")

    assert refreshed.status_code == 200
    assert first_cookie != rotated_cookie
    assert reused.status_code == 401
    assert logged_out.status_code == 204
    assert after_logout.status_code == 401
