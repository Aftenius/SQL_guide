"""SQLAlchemy unit of work."""

from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sql_guide.domain.ports import (
    LearnerProfileRepository,
    RefreshTokenRepository,
    UserRepository,
)
from sql_guide.infrastructure.persistence.repositories import (
    SqlLearnerProfileRepository,
    SqlRefreshTokenRepository,
    SqlUserRepository,
)


class SqlAlchemyUnitOfWork:
    """One database transaction for account and progress writes."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Open a session and bind repositories to it.

        Args:
            session_factory: Factory created from the application engine.
        """
        self._session = session_factory()
        self.users: UserRepository = SqlUserRepository(self._session)
        self.profiles: LearnerProfileRepository = SqlLearnerProfileRepository(
            self._session
        )
        self.refresh_tokens: RefreshTokenRepository = SqlRefreshTokenRepository(
            self._session
        )

    async def __aenter__(self) -> Self:
        """Start using the transaction.

        Returns:
            This unit of work.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        """Roll back on failure and always close the session.

        Args:
            exc_type: Exception type when the body failed.
            exc: Exception instance when the body failed.
            traceback: Traceback when the body failed.
        """
        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()

    async def commit(self) -> None:
        """Commit the open transaction."""
        await self._session.commit()


class SqlAlchemyUnitOfWorkFactory:
    """Opens a SQLAlchemy unit of work for each use case call."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Store the session factory.

        Args:
            session_factory: Factory created from the application engine.
        """
        self._session_factory = session_factory

    def __call__(self) -> SqlAlchemyUnitOfWork:
        """Open a new unit of work.

        Returns:
            A unit of work bound to a fresh session.
        """
        return SqlAlchemyUnitOfWork(self._session_factory)
