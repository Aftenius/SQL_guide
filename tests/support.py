"""Shared fixtures for identity tests."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sql_guide.application.health import GetHealthStatus
from sql_guide.application.learner_model import (
    CheckLearnerModel,
    ClearLearnerModel,
    DescribeLearnerModel,
    ReadLearnerModelKey,
    SaveLearnerModel,
)
from sql_guide.application.practice import GetPracticeCalendar, RecordSolve
from sql_guide.application.register_user import RegisterUser
from sql_guide.application.run_query import RunPracticeQuery
from sql_guide.application.sessions import (
    GetCurrentLearner,
    LoginUser,
    LogoutUser,
    RefreshSession,
)
from sql_guide.application.yandex_sign_in import SignInWithYandex
from sql_guide.domain.sandbox import QueryResult
from sql_guide.infrastructure.config import Settings
from sql_guide.infrastructure.container import AppContainer
from sql_guide.infrastructure.model_cipher import FernetModelCipher
from sql_guide.infrastructure.persistence.memory import InMemoryUnitOfWorkFactory
from sql_guide.infrastructure.security import (
    BcryptPasswordHasher,
    JwtAccessTokenIssuer,
    SecretRefreshTokenFactory,
    UuidIdGenerator,
)
from tests.fake_model import FakeModelProbe
from tests.fake_yandex import FakeYandexClient


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
    yandex: FakeYandexClient
    sign_in_with_yandex: SignInWithYandex
    model_probe: FakeModelProbe
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
    yandex = FakeYandexClient()
    model_probe = FakeModelProbe()
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
        yandex=yandex,
        sign_in_with_yandex=SignInWithYandex(
            factory,
            yandex,
            UuidIdGenerator(),
            clock,
            access_tokens,
            refresh_tokens,
            refresh_ttl,
        ),
        model_probe=model_probe,
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
        yandex=harness.yandex,
        sign_in_with_yandex=harness.sign_in_with_yandex,
        record_solve=RecordSolve(harness.factory, harness.clock),
        get_practice_calendar=GetPracticeCalendar(harness.factory, harness.clock),
        describe_learner_model=DescribeLearnerModel(harness.factory),
        save_learner_model=SaveLearnerModel(
            harness.factory,
            _test_cipher(),
            harness.clock,
        ),
        clear_learner_model=ClearLearnerModel(harness.factory),
        check_learner_model=CheckLearnerModel(
            harness.factory,
            _test_cipher(),
            harness.model_probe,
        ),
        read_learner_model_key=ReadLearnerModelKey(harness.factory, _test_cipher()),
        run_practice_query=RunPracticeQuery(_QuietSandbox()),
    )


class _QuietSandbox:
    """Sandbox double that returns no rows. Tests that need rows bring their own."""

    async def execute(self, setup: object, statement: str) -> QueryResult:
        """Ignore the statement and return an empty result."""
        del setup, statement
        return QueryResult((), ())


def _test_cipher() -> FernetModelCipher:
    return FernetModelCipher("test-secret-must-be-at-least-32-bytes")
