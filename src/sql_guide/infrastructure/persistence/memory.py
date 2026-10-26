"""In-memory unit of work used by application tests."""

import copy
from typing import Self
from uuid import UUID

from sql_guide.domain.errors import EmailAlreadyRegistered, YandexSignInFailed
from sql_guide.domain.external import ExternalIdentity
from sql_guide.domain.learner import LearnerProfile
from sql_guide.domain.ports import (
    ExternalIdentityRepository,
    LearnerProfileRepository,
    RefreshTokenRepository,
    UserRepository,
)
from sql_guide.domain.session import StoredRefreshToken
from sql_guide.domain.user import Email, User, UserId


class MemoryStore:
    """Shared identity state for one test."""

    def __init__(self) -> None:
        """Start with empty accounts, profiles, and sessions."""
        self.users: dict[UUID, User] = {}
        self.profiles: dict[UUID, LearnerProfile] = {}
        self.refresh_tokens: dict[str, StoredRefreshToken] = {}
        self.identities: dict[tuple[str, str], ExternalIdentity] = {}


class InMemoryUserRepository:
    """Account repository over a memory store."""

    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    async def add(self, user: User) -> None:
        """Insert an account or reject a duplicate email."""
        for existing in self._store.users.values():
            if existing.email == user.email:
                raise EmailAlreadyRegistered
        self._store.users[user.id.value] = user

    async def get_by_email(self, email: Email) -> User | None:
        """Return the account with this email."""
        for user in self._store.users.values():
            if user.email == email:
                return user
        return None

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Return the account with this id."""
        return self._store.users.get(user_id.value)


class InMemoryProfileRepository:
    """Progress-root repository over a memory store."""

    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    async def add(self, profile: LearnerProfile) -> None:
        """Insert a progress root."""
        self._store.profiles[profile.user_id.value] = profile

    async def get(self, user_id: UserId) -> LearnerProfile | None:
        """Return the progress root for an account."""
        return self._store.profiles.get(user_id.value)


class InMemoryRefreshTokenRepository:
    """Refresh-token repository over a memory store."""

    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    async def add(self, token: StoredRefreshToken) -> None:
        """Insert a refresh-token digest."""
        self._store.refresh_tokens[token.token_hash] = token

    async def get(self, token_hash: str) -> StoredRefreshToken | None:
        """Return a stored refresh token."""
        return self._store.refresh_tokens.get(token_hash)

    async def delete(self, token_hash: str) -> None:
        """Remove a refresh token when it exists."""
        self._store.refresh_tokens.pop(token_hash, None)


class InMemoryExternalIdentityRepository:
    """Provider-link repository over a memory store."""

    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    async def add(self, identity: ExternalIdentity) -> None:
        """Insert a provider link or reject a duplicate subject."""
        key = (identity.provider, identity.subject)
        if key in self._store.identities:
            raise YandexSignInFailed
        self._store.identities[key] = identity

    async def get(self, provider: str, subject: str) -> ExternalIdentity | None:
        """Return the link for a provider subject."""
        return self._store.identities.get((provider, subject))


class InMemoryUnitOfWork:
    """Transaction over a memory store, restored when the body fails."""

    def __init__(self, store: MemoryStore) -> None:
        """Bind repositories to the shared store.

        Args:
            store: State shared by every unit of work in one test.
        """
        self._store = store
        self.users: UserRepository = InMemoryUserRepository(store)
        self.profiles: LearnerProfileRepository = InMemoryProfileRepository(store)
        self.refresh_tokens: RefreshTokenRepository = InMemoryRefreshTokenRepository(
            store
        )
        identities = InMemoryExternalIdentityRepository(store)
        self.identities: ExternalIdentityRepository = identities
        self._snapshot = copy.deepcopy(store)

    async def __aenter__(self) -> Self:
        """Remember the state from before this transaction.

        Returns:
            This unit of work.
        """
        self._snapshot = copy.deepcopy(self._store)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        """Restore the snapshot when the body raised.

        Args:
            exc_type: Exception type when the body failed.
            exc: Exception instance when the body failed.
            traceback: Traceback when the body failed.
        """
        if exc_type is not None:
            self._store.users.clear()
            self._store.users.update(self._snapshot.users)
            self._store.profiles.clear()
            self._store.profiles.update(self._snapshot.profiles)
            self._store.refresh_tokens.clear()
            self._store.refresh_tokens.update(self._snapshot.refresh_tokens)
            self._store.identities.clear()
            self._store.identities.update(self._snapshot.identities)

    async def commit(self) -> None:
        """Keep the current memory state."""
        self._snapshot = copy.deepcopy(self._store)


class InMemoryUnitOfWorkFactory:
    """Opens units of work that share one memory store."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        """Create or adopt the shared store.

        Args:
            store: Existing store. A new one is created when omitted.
        """
        self.store = store if store is not None else MemoryStore()

    def __call__(self) -> InMemoryUnitOfWork:
        """Open a unit of work on the shared store.

        Returns:
            A unit of work bound to this factory's store.
        """
        return InMemoryUnitOfWork(self.store)
