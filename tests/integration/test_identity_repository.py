"""Identity persistence against PostgreSQL."""

import asyncio
from datetime import timedelta

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from sql_guide.application.identity import LoginCommand, RegisterCommand
from sql_guide.application.register_user import RegisterUser
from sql_guide.application.sessions import GetCurrentLearner, LoginUser
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

_TEST_DATABASE = "sql_guide_test"
_ADMIN_URL = "postgresql+psycopg://sql_guide:sql_guide@127.0.0.1:5433/sql_guide"
_TEST_URL = f"postgresql+psycopg://sql_guide:sql_guide@127.0.0.1:5433/{_TEST_DATABASE}"


async def _prepare_database() -> None:
    safe_name = _TEST_DATABASE.isidentifier()
    safe_url = _TEST_URL.endswith(f"/{_TEST_DATABASE}")
    if not safe_name or not safe_url:
        message = "Refusing to reset a database that is not the test database"
        raise RuntimeError(message)
    admin = create_async_engine(_ADMIN_URL, poolclass=NullPool)
    try:
        async with admin.connect() as connection:
            autocommit = await connection.execution_options(
                isolation_level="AUTOCOMMIT"
            )
            exists = await autocommit.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": _TEST_DATABASE},
            )
            if exists is None:
                await autocommit.execute(text(f"CREATE DATABASE {_TEST_DATABASE}"))
    except (OSError, SQLAlchemyError) as exc:
        pytest.skip(f"PostgreSQL is not available: {exc}")
    finally:
        await admin.dispose()

    engine = create_async_engine(_TEST_URL)
    async with engine.begin() as db:
        await db.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await db.execute(text("CREATE SCHEMA public"))
    await engine.dispose()

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", _TEST_URL)
    command.upgrade(config, "head")


@pytest.fixture(scope="module")
def migrated_database() -> str:
    """Create the test database and apply the identity migration."""
    asyncio.run(_prepare_database())
    return _TEST_URL


async def test_register_and_login_roundtrip(migrated_database: str) -> None:
    """The migration stores an account, its profile, and a working session."""
    engine = create_async_engine(migrated_database)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    unit_of_work = SqlAlchemyUnitOfWorkFactory(session_factory)
    clock = SystemClock()
    hasher = BcryptPasswordHasher(rounds=4)
    access_tokens = JwtAccessTokenIssuer(
        "test-secret-must-be-at-least-32-bytes",
        ttl_minutes=15,
        clock=clock,
    )
    refresh_tokens = SecretRefreshTokenFactory()
    register_user = RegisterUser(unit_of_work, hasher, UuidIdGenerator(), clock)
    login_user = LoginUser(
        unit_of_work,
        hasher,
        access_tokens,
        refresh_tokens,
        clock,
        timedelta(days=14),
    )
    current = GetCurrentLearner(unit_of_work, access_tokens)

    registered = await register_user.execute(
        RegisterCommand(email="ada@example.com", password="password123")
    )
    session = await login_user.execute(
        LoginCommand(email="ada@example.com", password="password123")
    )
    learner = await current.execute(session.access_token)
    await engine.dispose()

    assert learner.id == registered.id
    assert learner.email == "ada@example.com"
