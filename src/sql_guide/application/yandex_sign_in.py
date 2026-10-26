"""Sign in with Yandex and keep progress on one account."""

from datetime import timedelta

from sql_guide.application.identity import SessionTokens
from sql_guide.application.sessions import issue_session
from sql_guide.domain.errors import YandexSignInFailed
from sql_guide.domain.external import YANDEX, ExternalIdentity
from sql_guide.domain.learner import LearnerProfile
from sql_guide.domain.ports import (
    AccessTokenIssuer,
    Clock,
    IdGenerator,
    RefreshTokenFactory,
    UnitOfWork,
    UnitOfWorkFactory,
)
from sql_guide.domain.user import Email, User, UserId
from sql_guide.domain.yandex import YandexClient


class SignInWithYandex:
    """Create or reuse an account from a Yandex authorization code."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        yandex: YandexClient,
        ids: IdGenerator,
        clock: Clock,
        access_tokens: AccessTokenIssuer,
        refresh_tokens: RefreshTokenFactory,
        refresh_ttl: timedelta,
    ) -> None:
        """Store the ports this use case needs.

        Args:
            uow_factory: Opens the transaction for the account and session.
            yandex: Exchanges the authorization code.
            ids: Supplies an id when a new account is created.
            clock: Supplies creation and expiry times.
            access_tokens: Issues the bearer token.
            refresh_tokens: Issues the cookie token.
            refresh_ttl: How long the refresh token stays valid.
        """
        self._uow_factory = uow_factory
        self._yandex = yandex
        self._ids = ids
        self._clock = clock
        self._access_tokens = access_tokens
        self._refresh_tokens = refresh_tokens
        self._refresh_ttl = refresh_ttl

    async def execute(self, code: str) -> SessionTokens:
        """Sign the learner in with Yandex.

        An existing Yandex link is reused. Otherwise an account with the same
        email is linked, or a new account and progress root are created.

        Args:
            code: Authorization code from the Yandex redirect.

        Returns:
            A new access token and refresh token.

        Raises:
            YandexSignInFailed: Yandex did not return a usable account.
            InvalidEmail: The Yandex email cannot be stored.
        """
        account = await self._yandex.exchange(code)
        email = Email.parse(account.email)
        async with self._uow_factory() as uow:
            linked = await uow.identities.get(YANDEX, account.subject)
            if linked is not None:
                user = await uow.users.get_by_id(linked.user_id)
                if user is None:
                    raise YandexSignInFailed
            else:
                user = await self._account_for_email(uow, email)
                await uow.identities.add(
                    ExternalIdentity(
                        provider=YANDEX,
                        subject=account.subject,
                        user_id=user.id,
                    )
                )
            return await issue_session(
                uow,
                user.id,
                self._access_tokens,
                self._refresh_tokens,
                self._clock,
                self._refresh_ttl,
            )

    async def _account_for_email(self, uow: UnitOfWork, email: Email) -> User:
        existing = await uow.users.get_by_email(email)
        if existing is not None:
            return existing
        created_at = self._clock.now()
        user = User(
            id=UserId(self._ids.new_id()),
            email=email,
            password_hash=None,
            created_at=created_at,
        )
        await uow.users.add(user)
        await uow.profiles.add(LearnerProfile(user_id=user.id, created_at=created_at))
        return user
