"""SQLAlchemy repositories for accounts and sessions."""

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from sql_guide.domain.errors import EmailAlreadyRegistered
from sql_guide.domain.learner import LearnerProfile
from sql_guide.domain.session import StoredRefreshToken
from sql_guide.domain.user import Email, User, UserId
from sql_guide.infrastructure.persistence.models import (
    LearnerProfileModel,
    RefreshTokenModel,
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
