"""Record a solved step and read the practice calendar."""

from dataclasses import dataclass
from datetime import date

from sql_guide.domain.ports import Clock, UnitOfWorkFactory
from sql_guide.domain.practice import (
    ReviewCard,
    SolvedDay,
    lesson_key,
    practice_date,
    schedule_solve,
    streak,
)
from sql_guide.domain.user import UserId


@dataclass(frozen=True, slots=True)
class RecordSolveCommand:
    """Step a learner marked as solved.

    Attributes:
        user_id: Account that owns the card.
        track: Course section slug.
        lesson: Step slug.
    """

    user_id: UserId
    track: str
    lesson: str


@dataclass(frozen=True, slots=True)
class SolveResult:
    """Card after a solve, including whether the day gained a mark.

    Attributes:
        card: Scheduled review.
        counted: Whether this call added a solve to the calendar day.
        today: Practice day used for the call.
    """

    card: ReviewCard
    counted: bool
    today: date


@dataclass(frozen=True, slots=True)
class PracticeOverview:
    """Calendar marks and upcoming reviews for one account.

    Attributes:
        today: Practice day used to draw the calendar.
        solved_days: Days that contain at least one solve.
        reviews: One card per solved step.
        streak: Consecutive solved days ending today or yesterday.
    """

    today: date
    solved_days: tuple[SolvedDay, ...]
    reviews: tuple[ReviewCard, ...]
    streak: int


class RecordSolve:
    """Count a solved step and schedule its next review."""

    def __init__(self, uow_factory: UnitOfWorkFactory, clock: Clock) -> None:
        """Store the collaborators.

        Args:
            uow_factory: Opens a transaction for the card and the day.
            clock: Source of the practice day.
        """
        self._uow_factory = uow_factory
        self._clock = clock

    async def execute(self, command: RecordSolveCommand) -> SolveResult:
        """Save the solve and the next due date.

        Args:
            command: Account and step slug.

        Returns:
            The scheduled card and whether the day was newly marked.
        """
        track = lesson_key(command.track)
        lesson = lesson_key(command.lesson)
        today = practice_date(self._clock.now())
        async with self._uow_factory() as uow:
            existing = await uow.practice.get_card(command.user_id, track, lesson)
            card, counted = schedule_solve(
                existing,
                user_id=command.user_id,
                track=track,
                lesson=lesson,
                on=today,
            )
            await uow.practice.save_card(card)
            if counted:
                await uow.practice.add_solve(command.user_id, today)
            await uow.commit()
        return SolveResult(card=card, counted=counted, today=today)


class GetPracticeCalendar:
    """Read solved days and review cards for the profile."""

    def __init__(self, uow_factory: UnitOfWorkFactory, clock: Clock) -> None:
        """Store the collaborators.

        Args:
            uow_factory: Opens a read of cards and solved days.
            clock: Source of the practice day.
        """
        self._uow_factory = uow_factory
        self._clock = clock

    async def execute(self, user_id: UserId) -> PracticeOverview:
        """Load the calendar for an account.

        Args:
            user_id: Account that owns the cards.

        Returns:
            Solved days, review cards, and the current streak.
        """
        today = practice_date(self._clock.now())
        async with self._uow_factory() as uow:
            solved_days = await uow.practice.solved_days(user_id)
            reviews = await uow.practice.list_cards(user_id)
        return PracticeOverview(
            today=today,
            solved_days=tuple(solved_days),
            reviews=tuple(reviews),
            streak=streak({day.on for day in solved_days}, today),
        )
