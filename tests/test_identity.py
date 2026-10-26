"""Registration, login, and progress without a database."""

import pytest

from sql_guide.application.identity import LoginCommand, RegisterCommand
from sql_guide.domain.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidEmail,
    InvalidToken,
    WeakPassword,
)
from tests.support import build_harness


async def test_register_creates_a_progress_root() -> None:
    """A new account gets a learner profile in the same transaction."""
    harness = build_harness()

    learner = await harness.register_user.execute(
        RegisterCommand(email="Ada@Example.com", password="password123")
    )

    assert learner.email == "ada@example.com"
    assert learner.profile_created_at == harness.clock.now()
    assert len(harness.factory.store.profiles) == 1


async def test_register_rejects_a_duplicate_email() -> None:
    """The second registration for an email does not add another profile."""
    harness = build_harness()
    command = RegisterCommand(email="ada@example.com", password="password123")
    await harness.register_user.execute(command)

    with pytest.raises(EmailAlreadyRegistered):
        await harness.register_user.execute(command)

    assert len(harness.factory.store.users) == 1
    assert len(harness.factory.store.profiles) == 1


@pytest.mark.parametrize(
    ("email", "password", "error"),
    [
        ("not-an-email", "password123", InvalidEmail),
        ("ada@example.com", "short", WeakPassword),
    ],
)
async def test_register_rejects_invalid_input(
    email: str,
    password: str,
    error: type[Exception],
) -> None:
    """Malformed email and a short password are refused before storage."""
    harness = build_harness()

    with pytest.raises(error):
        await harness.register_user.execute(
            RegisterCommand(email=email, password=password)
        )

    assert harness.factory.store.users == {}


async def test_login_rejects_unknown_and_wrong_password() -> None:
    """Unknown email and a wrong password share one failure."""
    harness = build_harness()
    await harness.register_user.execute(
        RegisterCommand(email="ada@example.com", password="password123")
    )

    with pytest.raises(InvalidCredentials):
        await harness.login_user.execute(
            LoginCommand(email="missing@example.com", password="password123")
        )
    with pytest.raises(InvalidCredentials):
        await harness.login_user.execute(
            LoginCommand(email="ada@example.com", password="wrong-password")
        )


async def test_session_reads_the_saved_profile_and_rotates() -> None:
    """Login, refresh, and logout keep progress attached to the account."""
    harness = build_harness()
    registered = await harness.register_user.execute(
        RegisterCommand(email="ada@example.com", password="password123")
    )
    session = await harness.login_user.execute(
        LoginCommand(email="ada@example.com", password="password123")
    )

    current = await harness.get_current_learner.execute(session.access_token)
    rotated = await harness.refresh_session.execute(session.refresh_token)

    assert current.id == registered.id
    assert current.profile_created_at == registered.profile_created_at
    with pytest.raises(InvalidToken):
        await harness.refresh_session.execute(session.refresh_token)

    await harness.logout_user.execute(rotated.refresh_token)
    with pytest.raises(InvalidToken):
        await harness.refresh_session.execute(rotated.refresh_token)
