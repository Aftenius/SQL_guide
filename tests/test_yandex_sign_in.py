"""Yandex sign-in links the provider subject to one progress root."""

from typing import cast

import pytest
from fastapi.testclient import TestClient

from sql_guide.application.identity import LoginCommand, RegisterCommand
from sql_guide.domain.errors import InvalidCredentials
from sql_guide.domain.user import Email
from sql_guide.domain.yandex import YandexAccount
from sql_guide.presentation.app import create_app
from tests.fake_yandex import FakeYandexClient
from tests.support import build_harness, build_test_container


async def test_new_yandex_account_gets_a_profile_without_a_password() -> None:
    harness = build_harness()
    harness.yandex.accounts["code"] = YandexAccount("subject-1", "ada@example.com")

    tokens = await harness.sign_in_with_yandex.execute("code")
    learner = await harness.get_current_learner.execute(tokens.access_token)

    assert learner.email == "ada@example.com"
    async with harness.factory() as uow:
        user = await uow.users.get_by_email(Email.parse("ada@example.com"))
    assert user is not None
    assert user.password_hash is None


async def test_same_yandex_subject_returns_the_same_user() -> None:
    harness = build_harness()
    harness.yandex.accounts["code"] = YandexAccount("subject-1", "ada@example.com")

    first = await harness.sign_in_with_yandex.execute("code")
    second = await harness.sign_in_with_yandex.execute("code")

    first_learner = await harness.get_current_learner.execute(first.access_token)
    second_learner = await harness.get_current_learner.execute(second.access_token)
    assert first_learner.id == second_learner.id


async def test_matching_email_attaches_yandex_to_the_password_account() -> None:
    harness = build_harness()
    await harness.register_user.execute(
        RegisterCommand(email="ada@example.com", password="correct horse")
    )
    harness.yandex.accounts["code"] = YandexAccount("subject-1", "ada@example.com")

    tokens = await harness.sign_in_with_yandex.execute("code")
    yandex_learner = await harness.get_current_learner.execute(tokens.access_token)
    password_tokens = await harness.login_user.execute(
        LoginCommand(email="ada@example.com", password="correct horse")
    )
    password_learner = await harness.get_current_learner.execute(
        password_tokens.access_token
    )

    assert yandex_learner.id == password_learner.id


async def test_yandex_only_account_cannot_use_a_password() -> None:
    harness = build_harness()
    harness.yandex.accounts["code"] = YandexAccount("subject-1", "ada@example.com")
    await harness.sign_in_with_yandex.execute("code")

    with pytest.raises(InvalidCredentials):
        await harness.login_user.execute(
            LoginCommand(email="ada@example.com", password="correct horse")
        )


def test_yandex_start_sets_the_state_cookie() -> None:
    with TestClient(create_app(build_test_container())) as client:
        response = client.get("/auth/yandex/start")

    assert response.status_code == 200
    assert "oauth.yandex.ru" in response.json()["authorization_url"]
    assert "oauth_state" in response.cookies


def test_yandex_callback_issues_a_session_when_the_state_matches() -> None:
    container = build_test_container()
    yandex = cast(FakeYandexClient, container.yandex)
    yandex.accounts["good-code"] = YandexAccount("subject-1", "ada@example.com")
    with TestClient(create_app(container)) as client:
        start = client.get("/auth/yandex/start")
        response = client.get(
            "/auth/yandex/callback",
            params={"code": "good-code", "state": start.cookies["oauth_state"]},
        )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "refresh_token" in response.cookies


def test_yandex_callback_rejects_a_mismatched_state() -> None:
    with TestClient(create_app(build_test_container())) as client:
        client.get("/auth/yandex/start")
        response = client.get(
            "/auth/yandex/callback",
            params={"code": "good-code", "state": "someone-else"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Yandex sign-in could not be confirmed"
