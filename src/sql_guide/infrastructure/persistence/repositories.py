"""SQLAlchemy repositories for accounts and sessions."""

from datetime import date
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from sql_guide.domain.errors import EmailAlreadyRegistered, YandexSignInFailed
from sql_guide.domain.external import ExternalIdentity
from sql_guide.domain.learner import LearnerProfile
from sql_guide.domain.learner_model import LearnerModel
from sql_guide.domain.practice import ReviewCard, SolvedDay
from sql_guide.domain.session import StoredRefreshToken
from sql_guide.domain.user import Email, User, UserId
from sql_guide.infrastructure.persistence.models import (
    ExternalIdentityModel,
    LearnerModelRow,
    LearnerProfileModel,
    PracticeDayModel,
    RefreshTokenModel,
    ReviewCardModel,
    UserModel,
)


def _to_user(row: UserModel) -> User:
    return User(
        id=UserId(row.id),
        email=Email(row.email),
        password_hash=row.password_hash,
        created_at=row.created_at,
    )


class SqlUserRepository:
    """Account repository backed by the current session."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to an open session.

        Args:
            session: Session owned by the unit of work.
        """
        self._session = session

    async def add(self, user: User) -> None:
        """Insert an account.

        Args:
            user: Account to store.

        Raises:
            EmailAlreadyRegistered: The email violates the unique constraint.
        """
        self._session.add(
            UserModel(
                id=user.id.value,
                email=user.email.value,
                password_hash=user.password_hash,
                created_at=user.created_at,
            )
        )
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise EmailAlreadyRegistered from exc

    async def get_by_email(self, email: Email) -> User | None:
        """Load an account by email.

        Args:
            email: Normalized email.

        Returns:
            The account, or None when it does not exist.
        """
        statement = select(UserModel).where(UserModel.email == email.value)
        row = (await self._session.execute(statement)).scalar_one_or_none()
        if row is None:
            return None
        return _to_user(row)

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Load an account by id.

        Args:
            user_id: Account id.

        Returns:
            The account, or None when it does not exist.
        """
        row = await self._session.get(UserModel, user_id.value)
        if row is None:
            return None
        return _to_user(row)


class SqlLearnerProfileRepository:
    """Progress-root repository backed by the current session."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to an open session.

        Args:
            session: Session owned by the unit of work.
        """
        self._session = session

    async def add(self, profile: LearnerProfile) -> None:
        """Insert a progress root.

        Args:
            profile: Progress root to store.
        """
        self._session.add(
            LearnerProfileModel(
                user_id=profile.user_id.value,
                created_at=profile.created_at,
            )
        )
        await self._session.flush()

    async def get(self, user_id: UserId) -> LearnerProfile | None:
        """Load the progress root for an account.

        Args:
            user_id: Account id.

        Returns:
            The progress root, or None when it does not exist.
        """
        row = await self._session.get(LearnerProfileModel, user_id.value)
        if row is None:
            return None
        return LearnerProfile(user_id=UserId(row.user_id), created_at=row.created_at)


class SqlRefreshTokenRepository:
    """Refresh-token repository backed by the current session."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to an open session.

        Args:
            session: Session owned by the unit of work.
        """
        self._session = session

    async def add(self, token: StoredRefreshToken) -> None:
        """Insert a refresh-token digest.

        Args:
            token: Digest and expiry to store.
        """
        self._session.add(
            RefreshTokenModel(
                token_hash=token.token_hash,
                user_id=token.user_id.value,
                expires_at=token.expires_at,
            )
        )
        await self._session.flush()

    async def get(self, token_hash: str) -> StoredRefreshToken | None:
        """Load a refresh token by its digest.

        Args:
            token_hash: SHA-256 hex digest.

        Returns:
            The stored token, or None when it does not exist.
        """
        row = await self._session.get(RefreshTokenModel, token_hash)
        if row is None:
            return None
        return StoredRefreshToken(
            token_hash=row.token_hash,
            user_id=UserId(row.user_id),
            expires_at=row.expires_at,
        )

    async def delete(self, token_hash: str) -> None:
        """Remove a refresh token digest.

        Args:
            token_hash: SHA-256 hex digest. A missing row is ignored.
        """
        statement = delete(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        )
        await self._session.execute(statement)


class SqlExternalIdentityRepository:
    """Provider-link repository backed by the current session."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to an open session.

        Args:
            session: Session owned by the unit of work.
        """
        self._session = session

    async def add(self, identity: ExternalIdentity) -> None:
        """Insert a provider link.

        Args:
            identity: Provider subject to attach.

        Raises:
            YandexSignInFailed: The provider subject is already stored.
        """
        self._session.add(
            ExternalIdentityModel(
                provider=identity.provider,
                subject=identity.subject,
                user_id=identity.user_id.value,
            )
        )
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise YandexSignInFailed from exc

    async def get(self, provider: str, subject: str) -> ExternalIdentity | None:
        """Load a provider link.

        Args:
            provider: Provider name.
            subject: Provider's stable user id.

        Returns:
            The link, or None when it does not exist.
        """
        row = await self._session.get(ExternalIdentityModel, (provider, subject))
        if row is None:
            return None
        return ExternalIdentity(
            provider=row.provider,
            subject=row.subject,
            user_id=UserId(row.user_id),
        )


class SqlPracticeRepository:
    """Solved days and review cards backed by the current session."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to an open session.

        Args:
            session: Session owned by the unit of work.
        """
        self._session = session

    async def get_card(
        self,
        user_id: UserId,
        track: str,
        lesson: str,
    ) -> ReviewCard | None:
        """Load the card for one step.

        Args:
            user_id: Account id.
            track: Course section slug.
            lesson: Step slug.

        Returns:
            The card, or None when the step has never been solved.
        """
        row = await self._session.get(
            ReviewCardModel,
            (user_id.value, track, lesson),
        )
        if row is None:
            return None
        return _to_card(row)

    async def save_card(self, card: ReviewCard) -> None:
        """Insert or replace the card for one step.

        Args:
            card: Scheduled review to store.
        """
        key = (card.user_id.value, card.track, card.lesson)
        row = await self._session.get(ReviewCardModel, key)
        if row is None:
            self._session.add(
                ReviewCardModel(
                    user_id=card.user_id.value,
                    track_slug=card.track,
                    lesson_slug=card.lesson,
                    ease=Decimal(f"{card.ease:.2f}"),
                    interval_days=card.interval_days,
                    repetitions=card.repetitions,
                    due_on=card.due_on,
                    last_reviewed_on=card.last_reviewed_on,
                )
            )
        else:
            row.ease = Decimal(f"{card.ease:.2f}")
            row.interval_days = card.interval_days
            row.repetitions = card.repetitions
            row.due_on = card.due_on
            row.last_reviewed_on = card.last_reviewed_on
        await self._session.flush()

    async def list_cards(self, user_id: UserId) -> list[ReviewCard]:
        """Load every review card for an account.

        Args:
            user_id: Account id.

        Returns:
            Cards ordered by the next due date.
        """
        statement = (
            select(ReviewCardModel)
            .where(ReviewCardModel.user_id == user_id.value)
            .order_by(ReviewCardModel.due_on, ReviewCardModel.lesson_slug)
        )
        rows = await self._session.scalars(statement)
        return [_to_card(row) for row in rows]

    async def solved_days(self, user_id: UserId) -> list[SolvedDay]:
        """Load every day that contains at least one solve.

        Args:
            user_id: Account id.

        Returns:
            Days ordered from oldest to newest.
        """
        statement = (
            select(PracticeDayModel)
            .where(PracticeDayModel.user_id == user_id.value)
            .order_by(PracticeDayModel.practiced_on)
        )
        rows = await self._session.scalars(statement)
        return [SolvedDay(on=row.practiced_on, solved=row.solved_count) for row in rows]

    async def add_solve(self, user_id: UserId, on: date) -> None:
        """Count one more solved step on a practice day.

        Args:
            user_id: Account id.
            on: Practice day that gains the solve.
        """
        row = await self._session.get(PracticeDayModel, (user_id.value, on))
        if row is None:
            self._session.add(
                PracticeDayModel(
                    user_id=user_id.value,
                    practiced_on=on,
                    solved_count=1,
                )
            )
        else:
            row.solved_count += 1
        await self._session.flush()


class SqlLearnerModelRepository:
    """Encrypted model keys backed by the current session."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to an open session.

        Args:
            session: Session owned by the unit of work.
        """
        self._session = session

    async def get(self, user_id: UserId) -> LearnerModel | None:
        """Load the saved model for an account.

        Args:
            user_id: Account id.

        Returns:
            The saved model, or None when it does not exist.
        """
        row = await self._session.get(LearnerModelRow, user_id.value)
        if row is None:
            return None
        return _to_learner_model(row)

    async def save(self, model: LearnerModel) -> None:
        """Insert or replace the saved model.

        Args:
            model: Encrypted key to store.
        """
        row = await self._session.get(LearnerModelRow, model.user_id.value)
        if row is None:
            self._session.add(
                LearnerModelRow(
                    user_id=model.user_id.value,
                    provider=model.provider,
                    model_name=model.model,
                    ciphertext=model.ciphertext,
                    hint=model.hint,
                    updated_at=model.updated_at,
                )
            )
        else:
            row.provider = model.provider
            row.model_name = model.model
            row.ciphertext = model.ciphertext
            row.hint = model.hint
            row.updated_at = model.updated_at
        await self._session.flush()

    async def delete(self, user_id: UserId) -> None:
        """Remove the saved model when it exists.

        Args:
            user_id: Account id.
        """
        row = await self._session.get(LearnerModelRow, user_id.value)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()


def _to_learner_model(row: LearnerModelRow) -> LearnerModel:
    return LearnerModel(
        user_id=UserId(row.user_id),
        provider=row.provider,
        model=row.model_name,
        ciphertext=row.ciphertext,
        hint=row.hint,
        updated_at=row.updated_at,
    )


def _to_card(row: ReviewCardModel) -> ReviewCard:
    return ReviewCard(
        user_id=UserId(row.user_id),
        track=row.track_slug,
        lesson=row.lesson_slug,
        ease=float(row.ease),
        interval_days=row.interval_days,
        repetitions=row.repetitions,
        due_on=row.due_on,
        last_reviewed_on=row.last_reviewed_on,
    )
