"""Solved days and the SM-2 schedule behind the profile calendar."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from sql_guide.application.practice import (
    GetPracticeCalendar,
    RecordSolve,
    RecordSolveCommand,
)
from sql_guide.domain.practice import practice_date, schedule_solve, streak
from sql_guide.domain.user import UserId
from sql_guide.infrastructure.persistence.memory import InMemoryUnitOfWorkFactory
from sql_guide.infrastructure.security import UuidIdGenerator
from sql_guide.presentation.app import create_app
from tests.support import FixedClock, build_test_container

_PASSWORD = "password123"
_WHEN = datetime(2026, 10, 26, 12, tzinfo=UTC)


def test_schedule_grows_and_ignores_a_second_solve_the_same_day() -> None:
    """The first three successes use the SM-2 intervals 1, 6, and 16 days."""
    user_id = UserId(UuidIdGenerator().new_id())
    today = practice_date(_WHEN)
    first, counted = schedule_solve(
        None,
        user_id=user_id,
        track="sql",
        lesson="select",
        on=today,
    )
    second, _ = schedule_solve(
        first,
        user_id=user_id,
        track="sql",
        lesson="select",
        on=today + timedelta(days=1),
    )
    third, _ = schedule_solve(
        second,
        user_id=user_id,
        track="sql",
        lesson="select",
        on=today + timedelta(days=7),
    )
    same_day, counted_again = schedule_solve(
        first,
        user_id=user_id,
        track="sql",
        lesson="select",
        on=today,
    )

    assert counted is True
    assert first.interval_days == 1
    assert first.due_on == today + timedelta(days=1)
    assert second.interval_days == 6
    assert third.interval_days == 16
    assert third.ease == 2.8
    assert counted_again is False
    assert same_day == first


def test_streak_stops_at_a_gap_and_allows_yesterday() -> None:
    """A missed day ends the run, and today can still be empty."""
    today = practice_date(_WHEN)
    assert streak({today, today - timedelta(days=1)}, today) == 2
    assert streak({today - timedelta(days=1), today - timedelta(days=2)}, today) == 2
    assert streak({today - timedelta(days=2)}, today) == 0


async def test_recording_a_solve_marks_the_day_once() -> None:
    """Two solves of one step on one day leave a single calendar mark."""
    factory = InMemoryUnitOfWorkFactory()
    clock = FixedClock(_WHEN)
    user_id = UserId(UuidIdGenerator().new_id())
    command = RecordSolveCommand(user_id=user_id, track="sql", lesson="select")
    record = RecordSolve(factory, clock)
    calendar = GetPracticeCalendar(factory, clock)

    first = await record.execute(command)
    second = await record.execute(command)
    overview = await calendar.execute(user_id)

    assert first.counted is True
    assert second.counted is False
    assert overview.streak == 1
    assert overview.solved_days[0].solved == 1
    assert overview.reviews[0].due_on == first.card.due_on


def test_practice_calendar_requires_a_session_and_stores_the_day() -> None:
    """The profile calendar is private and shows a recorded solve."""
    with TestClient(create_app(build_test_container())) as client:
        client.post(
            "/auth/register",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        logged_in = client.post(
            "/auth/login",
            json={"email": "ada@example.com", "password": _PASSWORD},
        )
        token = logged_in.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        denied = client.get("/me/practice")
        saved = client.post(
            "/me/practice",
            headers=headers,
            json={"track": "sql", "lesson": "select"},
        )
        calendar = client.get("/me/practice", headers=headers)
        invalid = client.post(
            "/me/practice",
            headers=headers,
            json={"track": "SQL", "lesson": "select"},
        )

    assert denied.status_code == 401
    assert saved.status_code == 200
    assert saved.json()["counted"] is True
    assert saved.json()["interval_days"] == 1
    assert calendar.status_code == 200
    assert calendar.json()["today"] == saved.json()["today"]
    assert calendar.json()["streak"] == 1
    assert calendar.json()["days"] == [{"date": saved.json()["today"], "solved": 1}]
    assert calendar.json()["reviews"][0]["lesson"] == "select"
    assert invalid.status_code == 422
