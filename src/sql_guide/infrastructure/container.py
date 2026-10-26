"""Composition root that wires use cases to adapters."""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from sql_guide.application.health import GetHealthStatus
from sql_guide.application.register_user import RegisterUser
from sql_guide.application.sessions import (
    GetCurrentLearner,
    LoginUser,
    LogoutUser,
    RefreshSession,
)
from sql_guide.application.yandex_sign_in import SignInWithYandex
from sql_guide.domain.yandex import YandexClient
from sql_guide.infrastructure.config import Settings, get_settings
from sql_guide.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWorkFactory,
)
from sql_guide.infrastructure.security import (
    BcryptPasswordHasher,
    JwtAccessTokenIssuer,
    SecretRefreshTokenFactory,
    SystemClock,
    UuidIdGenerator,
)
from sql_guide.infrastructure.yandex import HttpxYandexClient


@dataclass(slots=True)
class AppContainer:
    """Use cases and process resources available to the HTTP layer.

    Attributes:
        settings: Runtime configuration.
        engine: Database engine, disposed when the process stops.
        get_health: Liveness use case.
        register_user: Registration use case.
        login_user: Password login use case.
        refresh_session: Refresh-token rotation use case.
        logout_user: Refresh-token revocation use case.
        get_current_learner: Bearer-token lookup use case.
        yandex: Client that builds the Yandex URL and exchanges codes.
        sign_in_with_yandex: Yandex sign-in use case.
    """

    settings: Settings
    engine: AsyncEngine | None
    get_health: GetHealthStatus
    register_user: RegisterUser
    login_user: LoginUser
    refresh_session: RefreshSession
    logout_user: LogoutUser
    get_current_learner: GetCurrentLearner
    yandex: YandexClient
    sign_in_with_yandex: SignInWithYandex


def build_container(settings: Settings | None = None) -> AppContainer:
    """Wire the production adapters.

    Args:
        settings: Explicit settings. When omitted, settings come from the environment.

    Returns:
        A container whose use cases share one database engine.
    """
    resolved = settings if settings is not None else get_settings()
    engine = create_async_engine(resolved.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    unit_of_work = SqlAlchemyUnitOfWorkFactory(session_factory)
    clock = SystemClock()
    hasher = BcryptPasswordHasher(resolved.password_hash_rounds)
    access_tokens = JwtAccessTokenIssuer(
        resolved.jwt_secret,
        resolved.access_token_ttl_minutes,
        clock,
    )
    refresh_tokens = SecretRefreshTokenFactory()
    refresh_ttl = timedelta(days=resolved.refresh_token_ttl_days)
    yandex = HttpxYandexClient(
        resolved.yandex_client_id,
        resolved.yandex_client_secret,
        resolved.yandex_redirect_uri,
    )
    return AppContainer(
        settings=resolved,
        engine=engine,
        get_health=GetHealthStatus(),
        register_user=RegisterUser(unit_of_work, hasher, UuidIdGenerator(), clock),
        login_user=LoginUser(
            unit_of_work,
            hasher,
            access_tokens,
            refresh_tokens,
            clock,
            refresh_ttl,
        ),
        refresh_session=RefreshSession(
            unit_of_work,
            access_tokens,
            refresh_tokens,
            clock,
            refresh_ttl,
        ),
        logout_user=LogoutUser(unit_of_work, refresh_tokens),
        get_current_learner=GetCurrentLearner(unit_of_work, access_tokens),
        yandex=yandex,
        sign_in_with_yandex=SignInWithYandex(
            unit_of_work,
            yandex,
            UuidIdGenerator(),
            clock,
            access_tokens,
            refresh_tokens,
            refresh_ttl,
        ),
    )
