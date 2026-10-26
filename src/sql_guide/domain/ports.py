"""Ports that infrastructure implements for identity and progress."""

from datetime import date, datetime
from types import TracebackType
from typing import Protocol
from uuid import UUID

from sql_guide.domain.external import ExternalIdentity
from sql_guide.domain.learner import LearnerProfile
from sql_guide.domain.learner_model import LearnerModel
from sql_guide.domain.practice import ReviewCard, SolvedDay
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


class PracticeRepository(Protocol):
    """Persistence for solved days and review cards."""

    async def get_card(
        self,
        user_id: UserId,
        track: str,
        lesson: str,
    ) -> ReviewCard | None:
        """Return the card for one step, if the learner has solved it."""
        ...

    async def save_card(self, card: ReviewCard) -> None:
        """Insert or replace the card for one step."""
        ...

    async def list_cards(self, user_id: UserId) -> list[ReviewCard]:
        """Return every review card for an account, earliest due date first."""
        ...

    async def solved_days(self, user_id: UserId) -> list[SolvedDay]:
        """Return every day that contains at least one solve."""
        ...

    async def add_solve(self, user_id: UserId, on: date) -> None:
        """Count one more solved step on a practice day."""
        ...


class LearnerModelRepository(Protocol):
    """Persistence for one encrypted model key per account."""

    async def get(self, user_id: UserId) -> LearnerModel | None:
        """Return the saved model, if the account has one."""
        ...

    async def save(self, model: LearnerModel) -> None:
        """Insert or replace the saved model."""
        ...

    async def delete(self, user_id: UserId) -> None:
        """Remove the saved model. A missing row is ignored."""
        ...


class ModelKeyCipher(Protocol):
    """Encryption for learner API keys."""

    def encrypt(self, secret: str) -> str:
        """Encrypt an API key for storage."""
        ...

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a stored API key.

        Raises:
            ModelKeyUnreadable: The ciphertext does not match the process secret.
        """
        ...


class ModelProbe(Protocol):
    """A check that the provider accepts a key. The key is not logged."""

    async def check(self, *, base_url: str, api_key: str, model: str) -> None:
        """Confirm the provider accepts the key for the model.

        Raises:
            ModelCheckFailed: The provider rejected the key or did not answer.
        """
        ...


class ExternalIdentityRepository(Protocol):
    """Persistence for provider sign-ins."""

    async def add(self, identity: ExternalIdentity) -> None:
        """Attach a provider subject to an account."""
        ...

    async def get(self, provider: str, subject: str) -> ExternalIdentity | None:
        """Return the link for a provider subject, if it exists."""
        ...


class UnitOfWork(Protocol):
    """One transaction covering account and progress writes."""

    users: UserRepository
    profiles: LearnerProfileRepository
    refresh_tokens: RefreshTokenRepository
    identities: ExternalIdentityRepository
    practice: PracticeRepository
    learner_models: LearnerModelRepository

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
