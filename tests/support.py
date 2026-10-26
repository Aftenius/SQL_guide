"""Shared fixtures for identity tests."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sql_guide.application.health import GetHealthStatus
from sql_guide.application.register_user import RegisterUser
from sql_guide.application.sessions import (
    GetCurrentLearner,
    LoginUser,
    LogoutUser,
    RefreshSession,
)
from sql_guide.infrastructure.config import Settings
from sql_guide.infrastructure.container import AppContainer
from sql_guide.infrastructure.persistence.memory import InMemoryUnitOfWorkFactory
from sql_guide.infrastructure.security import (
    BcryptPasswordHasher,
    JwtAccessTokenIssuer,
    SecretRefreshTokenFactory,
    UuidIdGenerator,
)


class FixedClock:
    """Clock frozen at one instant."""

    def __init__(self, instant: datetime) -> None:
        """Store the instant returned by every read.

        Args:
            instant: Timezone-aware moment.
        """
        self._instant = instant

    def now(self) -> datetime:
        """Return the frozen instant.

        Returns:
            The instant passed to the constructor.
        """
        return self._instant


@dataclass(slots=True)
class IdentityHarness:
    """Use cases sharing one in-memory store."""

    factory: InMemoryUnitOfWorkFactory
    register_user: RegisterUser
    login_user: LoginUser
    refresh_session: RefreshSession
    logout_user: LogoutUser
    get_current_learner: GetCurrentLearner
    clock: FixedClock


def build_harness() -> IdentityHarness:
    """Wire identity use cases to memory and fast password hashing.

    Returns:
        Use cases that do not touch PostgreSQL.
    """
    factory = InMemoryUnitOfWorkFactory()
    clock = FixedClock(datetime.now(UTC))
    hasher = BcryptPasswordHasher(rounds=4)
    access_tokens = JwtAccessTokenIssuer(
        "test-secret-must-be-at-least-32-bytes",
        ttl_minutes=15,
        clock=clock,
    )
    refresh_tokens = SecretRefreshTokenFactory()
    refresh_ttl = timedelta(days=14)
    return IdentityHarness(
        factory=factory,
        register_user=RegisterUser(factory, hasher, UuidIdGenerator(), clock),
        login_user=LoginUser(
            factory,
            hasher,
            access_tokens,
            refresh_tokens,
            clock,
            refresh_ttl,
        ),
        refresh_session=RefreshSession(
            factory,
            access_tokens,
            refresh_tokens,
            clock,
            refresh_ttl,
        ),
        logout_user=LogoutUser(factory, refresh_tokens),
        get_current_learner=GetCurrentLearner(factory, access_tokens),
        clock=clock,
    )


def build_test_container() -> AppContainer:
    """Build an HTTP container that keeps accounts in memory.

    Returns:
        A container safe to use without PostgreSQL.
    """
    harness = build_harness()
    settings = Settings(
        app_name="SQL Guide Test",
        database_url="postgresql+psycopg://unused",
        jwt_secret="test-secret-must-be-at-least-32-bytes",
        password_hash_rounds=4,
    )
    return AppContainer(
        settings=settings,
        engine=None,
        get_health=GetHealthStatus(),
        register_user=harness.register_user,
        login_user=harness.login_user,
        refresh_session=harness.refresh_session,
        logout_user=harness.logout_user,
        get_current_learner=harness.get_current_learner,
    )
