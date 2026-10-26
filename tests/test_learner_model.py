"""Profile storage for a learner's model key."""

import asyncio
from typing import cast
from uuid import UUID

from fastapi.testclient import TestClient

from sql_guide.domain.user import UserId
from sql_guide.presentation.app import create_app
from tests.fake_model import FakeModelProbe
from tests.support import build_test_container

_PASSWORD = "password123"
_KEY = "sk-" + ("a" * 24)


def test_saved_model_hides_the_key_and_keeps_it_for_the_server() -> None:
    """The profile shows a hint, and the server can still decrypt the key."""
    container = build_test_container()
    with TestClient(create_app(container)) as client:
        created = client.post(
            "/auth/register",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        logged_in = client.post(
            "/auth/login",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        headers = {"Authorization": f"Bearer {logged_in.json()['access_token']}"}
        denied = client.get("/me/model")
        saved = client.put(
            "/me/model",
            headers=headers,
            json={"provider": "deepseek", "model": "deepseek-chat", "api_key": _KEY},
        )
        described = client.get("/me/model", headers=headers)
        kept = client.put(
            "/me/model",
            headers=headers,
            json={"provider": "deepseek", "model": "deepseek-reasoner", "api_key": ""},
        )
        missing = client.put(
            "/me/model",
            headers={"Authorization": "Bearer " + logged_in.json()["access_token"]},
            json={"provider": "openai", "model": "gpt-4o", "api_key": _KEY},
        )

    user_id = UserId(UUID(created.json()["id"]))
    opened = asyncio.run(container.read_learner_model_key.execute(user_id))
    assert opened is not None
    choice, key = opened
    body = f"{saved.text} {described.text} {kept.text}"
    assert denied.status_code == 401
    assert saved.status_code == 200
    assert _KEY not in body
    assert described.json()["hint"] == _KEY[-4:]
    assert kept.json()["model"] == "deepseek-reasoner"
    assert key == _KEY
    assert choice is not None
    assert choice.model == "deepseek-reasoner"
    assert missing.status_code == 422


def test_check_uses_the_saved_key_and_delete_removes_it() -> None:
    """A check without a new key uses the stored one, then delete clears it."""
    container = build_test_container()
    probe = cast(FakeModelProbe, container.check_learner_model.probe)
    with TestClient(create_app(container)) as client:
        client.post(
            "/auth/register",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        logged_in = client.post(
            "/auth/login",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        headers = {"Authorization": f"Bearer {logged_in.json()['access_token']}"}
        client.put(
            "/me/model",
            headers=headers,
            json={"provider": "deepseek", "model": "deepseek-chat", "api_key": _KEY},
        )
        checked = client.post(
            "/me/model/check",
            headers=headers,
            json={"provider": "deepseek", "model": "deepseek-chat", "api_key": ""},
        )
        removed = client.delete("/me/model", headers=headers)
        empty = client.get("/me/model", headers=headers)

    assert checked.status_code == 204
    assert probe.calls == [("https://api.deepseek.com", _KEY, "deepseek-chat")]
    assert removed.status_code == 204
    assert empty.json() == {"configured": False}


def test_check_reports_a_rejected_key() -> None:
    """A provider rejection becomes a profile error and does not echo the key."""
    container = build_test_container()
    cast(FakeModelProbe, container.check_learner_model.probe).fail = True
    with TestClient(create_app(container)) as client:
        client.post(
            "/auth/register",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        logged_in = client.post(
            "/auth/login",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        rejected = client.post(
            "/me/model/check",
            headers={"Authorization": f"Bearer {logged_in.json()['access_token']}"},
            json={"provider": "deepseek", "model": "deepseek-chat", "api_key": _KEY},
        )

    assert rejected.status_code == 400
    assert _KEY not in rejected.text
