"""Ports that infrastructure implements for identity and progress."""

from datetime import datetime
from types import TracebackType
from typing import Protocol
from uuid import UUID

from sql_guide.domain.learner import LearnerProfile
from sql_guide.domain.session import StoredRefreshToken
from sql_guide.domain.user import Email, User, UserId


class Clock(Protocol):
    """Source of the current time."""

    def now(self) -> datetime:
        """Return the current timezone-aware instant."""
        ...


class IdGenerator(Protocol):
    """Source of new account identifiers."""

    def new_id(self) -> UUID:
        """Return a new identifier."""
        ...


class PasswordHasher(Protocol):
    """One-way password hashing."""

    def hash(self, password: str) -> str:
        """Hash a plain password."""
        ...

    def verify(self, password: str, password_hash: str) -> bool:
        """Return whether the plain password matches the stored hash."""
        ...


class AccessTokenIssuer(Protocol):
    """Short-lived access tokens."""

    def issue(self, user_id: UserId) -> str:
        """Create an access token for an account."""
        ...

    def read(self, token: str) -> UserId:
        """Read the account id from a valid access token."""
        ...


class RefreshTokenFactory(Protocol):
    """Opaque refresh tokens and their stored digests."""

    def issue(self) -> str:
        """Create a new opaque refresh token."""
        ...

    def hash(self, token: str) -> str:
        """Digest a refresh token for storage and lookup."""
        ...


class UserRepository(Protocol):
    """Persistence for accounts."""

    async def add(self, user: User) -> None:
        """Persist an account.

        Raises:
            EmailAlreadyRegistered: The email is already stored.
        """
        ...

    async def get_by_email(self, email: Email) -> User | None:
        """Return the account for an email, if it exists."""
        ...

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Return the account for an id, if it exists."""
        ...


class LearnerProfileRepository(Protocol):
    """Persistence for progress roots."""

    async def add(self, profile: LearnerProfile) -> None:
        """Persist a new progress root."""
        ...

    async def get(self, user_id: UserId) -> LearnerProfile | None:
        """Return the progress root for an account, if it exists."""
        ...


class RefreshTokenRepository(Protocol):
    """Persistence for refresh tokens."""

    async def add(self, token: StoredRefreshToken) -> None:
        """Persist a refresh token digest."""
        ...

    async def get(self, token_hash: str) -> StoredRefreshToken | None:
        """Return a stored refresh token by its digest."""
        ...

    async def delete(self, token_hash: str) -> None:
        """Remove a refresh token digest. Missing tokens are ignored."""
        ...


class UnitOfWork(Protocol):
    """One transaction covering account and progress writes."""

    users: UserRepository
    profiles: LearnerProfileRepository
    refresh_tokens: RefreshTokenRepository

    async def commit(self) -> None:
        """Make the transaction durable."""
        ...

    async def __aenter__(self) -> "UnitOfWork":
        """Start the transaction."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the transaction, rolling back when the body failed."""
        ...


class UnitOfWorkFactory(Protocol):
    """Opens a unit of work."""

    def __call__(self) -> UnitOfWork:
        """Return a unit of work that supports ``async with``."""
        ...
