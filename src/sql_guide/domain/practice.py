"""Solved days and the SM-2 schedule that follows them."""

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sql_guide.domain.errors import InvalidLessonKey
from sql_guide.domain.user import UserId

_MOSCOW = ZoneInfo("Europe/Moscow")
_LESSON_KEY = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_INITIAL_EASE = 2.5
_MIN_EASE = 1.3


@dataclass(frozen=True, slots=True)
class ReviewCard:
    """One lesson step and the date it should be practiced again.

    Attributes:
        user_id: Account that solved the step.
        track: Course section slug.
        lesson: Step slug.
        ease: SM-2 ease factor.
        interval_days: Days until the following review.
        repetitions: Successful reviews in the current streak.
        due_on: Calendar day of the next review.
        last_reviewed_on: Calendar day of the latest solve.
    """

    user_id: UserId
    track: str
    lesson: str
    ease: float
    interval_days: int
    repetitions: int
    due_on: date
    last_reviewed_on: date


@dataclass(frozen=True, slots=True)
class SolvedDay:
    """How many distinct steps were solved on one calendar day.

    Attributes:
        on: Calendar day in the practice timezone.
        solved: Number of steps counted that day.
    """

    on: date
    solved: int


def practice_date(instant: datetime) -> date:
    """Return the practice calendar day for an instant.

    Args:
        instant: Timezone-aware moment.

    Returns:
        The date in Europe/Moscow.
    """
    return instant.astimezone(_MOSCOW).date()


def lesson_key(raw: str) -> str:
    """Accept a course slug.

    Args:
        raw: Track or lesson slug from the client.

    Returns:
        The same slug when it is a short lowercase token.

    Raises:
        InvalidLessonKey: The slug is empty or contains other characters.
    """
    if len(raw) > 64 or _LESSON_KEY.fullmatch(raw) is None:
        raise InvalidLessonKey
    return raw


def schedule_solve(
    card: ReviewCard | None,
    *,
    user_id: UserId,
    track: str,
    lesson: str,
    on: date,
) -> tuple[ReviewCard, bool]:
    """Move a card forward after a successful solve.

    The first success is due the next day, the second after six days, and
    later successes multiply the interval by the ease factor. A second solve
    of the same step on the same day does not move the card.

    Args:
        card: Existing card, or None when the step is new.
        user_id: Account that solved the step.
        track: Course section slug.
        lesson: Step slug.
        on: Practice day of this solve.

    Returns:
        The card to store and whether this solve counts on ``on``.
    """
    if card is not None and card.last_reviewed_on == on:
        return card, False
    ease = _INITIAL_EASE if card is None else card.ease
    repetitions = 0 if card is None else card.repetitions
    interval = 0 if card is None else card.interval_days
    if repetitions == 0:
        interval = 1
    elif repetitions == 1:
        interval = 6
    else:
        interval = max(1, round(interval * ease))
    ease = round(max(_MIN_EASE, ease + 0.1), 2)
    updated = ReviewCard(
        user_id=user_id,
        track=track,
        lesson=lesson,
        ease=ease,
        interval_days=interval,
        repetitions=repetitions + 1,
        due_on=on + timedelta(days=interval),
        last_reviewed_on=on,
    )
    return updated, True


def streak(solved_on: set[date], today: date) -> int:
    """Count the unbroken run of solved days ending today or yesterday.

    Args:
        solved_on: Days that contain at least one solve.
        today: Practice day used as the end of the run.

    Returns:
        The number of consecutive solved days.
    """
    cursor = today if today in solved_on else today - timedelta(days=1)
    count = 0
    while cursor in solved_on:
        count += 1
        cursor -= timedelta(days=1)
    return count
