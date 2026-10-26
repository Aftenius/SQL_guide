"""Open, rotate, and close a learner session."""

from datetime import timedelta

from sql_guide.application.identity import LearnerView, LoginCommand, SessionTokens
from sql_guide.domain.errors import InvalidCredentials, InvalidToken
from sql_guide.domain.ports import (
    AccessTokenIssuer,
    Clock,
    PasswordHasher,
    RefreshTokenFactory,
    UnitOfWork,
    UnitOfWorkFactory,
)
from sql_guide.domain.session import StoredRefreshToken
from sql_guide.domain.user import Email, UserId


class LoginUser:
    """Check a password and issue a session."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        hasher: PasswordHasher,
        access_tokens: AccessTokenIssuer,
        refresh_tokens: RefreshTokenFactory,
        clock: Clock,
        refresh_ttl: timedelta,
    ) -> None:
        """Store the ports this use case needs.

        Args:
            uow_factory: Opens the transaction that stores the refresh token.
            hasher: Checks the plain password against the stored hash.
            access_tokens: Issues the bearer token.
            refresh_tokens: Issues and digests the cookie token.
            clock: Supplies the current time.
            refresh_ttl: How long the refresh token stays valid.
        """
        self._uow_factory = uow_factory
        self._hasher = hasher
        self._access_tokens = access_tokens
        self._refresh_tokens = refresh_tokens
        self._clock = clock
        self._refresh_ttl = refresh_ttl

    async def execute(self, command: LoginCommand) -> SessionTokens:
        """Log a learner in.

        Args:
            command: Email and password from the login form.

        Returns:
            A new access token and refresh token.

        Raises:
            InvalidCredentials: The email is unknown or the password is wrong.
            InvalidEmail: The email is malformed.
        """
        email = Email.parse(command.email)
        async with self._uow_factory() as uow:
            user = await uow.users.get_by_email(email)
            stored_hash = None if user is None else user.password_hash
            password_matches = stored_hash is not None and self._hasher.verify(
                command.password,
                stored_hash,
            )
            if user is None or not password_matches:
                raise InvalidCredentials
            return await issue_session(
                uow,
                user.id,
                self._access_tokens,
                self._refresh_tokens,
                self._clock,
                self._refresh_ttl,
            )


class RefreshSession:
    """Replace a refresh token with a new pair."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        access_tokens: AccessTokenIssuer,
        refresh_tokens: RefreshTokenFactory,
        clock: Clock,
        refresh_ttl: timedelta,
    ) -> None:
        """Store the ports this use case needs.

        Args:
            uow_factory: Opens the transaction that rotates the token.
            access_tokens: Issues the next bearer token.
            refresh_tokens: Digests and issues cookie tokens.
            clock: Supplies the current time.
            refresh_ttl: How long the replacement refresh token stays valid.
        """
        self._uow_factory = uow_factory
        self._access_tokens = access_tokens
        self._refresh_tokens = refresh_tokens
        self._clock = clock
        self._refresh_ttl = refresh_ttl

    async def execute(self, refresh_token: str) -> SessionTokens:
        """Rotate a refresh token.

        Args:
            refresh_token: Opaque token from the cookie.

        Returns:
            A new access token and refresh token.

        Raises:
            InvalidToken: The token is unknown or expired.
        """
        token_hash = self._refresh_tokens.hash(refresh_token)
        async with self._uow_factory() as uow:
            stored = await uow.refresh_tokens.get(token_hash)
            if stored is None or stored.expires_at <= self._clock.now():
                raise InvalidToken
            await uow.refresh_tokens.delete(token_hash)
            return await issue_session(
                uow,
                stored.user_id,
                self._access_tokens,
                self._refresh_tokens,
                self._clock,
                self._refresh_ttl,
            )


class LogoutUser:
    """Revoke the refresh token for the current cookie."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        refresh_tokens: RefreshTokenFactory,
    ) -> None:
        """Store the ports this use case needs.

        Args:
            uow_factory: Opens the transaction that deletes the token.
            refresh_tokens: Digests the cookie token.
        """
        self._uow_factory = uow_factory
        self._refresh_tokens = refresh_tokens

    async def execute(self, refresh_token: str | None) -> None:
        """Revoke a refresh token when one was sent.

        Args:
            refresh_token: Opaque token from the cookie, if the cookie exists.
        """
        if refresh_token is None or refresh_token == "":
            return
        token_hash = self._refresh_tokens.hash(refresh_token)
        async with self._uow_factory() as uow:
            await uow.refresh_tokens.delete(token_hash)
            await uow.commit()


class GetCurrentLearner:
    """Load the account and progress root for a bearer token."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        access_tokens: AccessTokenIssuer,
    ) -> None:
        """Store the ports this use case needs.

        Args:
            uow_factory: Opens a read of the account and profile.
            access_tokens: Reads the account id from the bearer token.
        """
        self._uow_factory = uow_factory
        self._access_tokens = access_tokens

    async def execute(self, access_token: str) -> LearnerView:
        """Return the learner represented by an access token.

        Args:
            access_token: Bearer token without the scheme prefix.

        Returns:
            The account and its progress root.

        Raises:
            InvalidToken: The token or the account behind it is not usable.
        """
        user_id = self._access_tokens.read(access_token)
        async with self._uow_factory() as uow:
            user = await uow.users.get_by_id(user_id)
            profile = None if user is None else await uow.profiles.get(user_id)
            if user is None or profile is None:
                raise InvalidToken
            return LearnerView(
                id=user.id.value,
                email=user.email.value,
                profile_created_at=profile.created_at,
            )


async def issue_session(
    uow: UnitOfWork,
    user_id: UserId,
    access_tokens: AccessTokenIssuer,
    refresh_tokens: RefreshTokenFactory,
    clock: Clock,
    refresh_ttl: timedelta,
) -> SessionTokens:
    """Store a new refresh token and return both session tokens.

    Args:
        uow: Open transaction that will store the refresh token.
        user_id: Account that owns the session.
        access_tokens: Issuer of the bearer token.
        refresh_tokens: Issuer of the cookie token.
        clock: Current time.
        refresh_ttl: Lifetime of the refresh token.

    Returns:
        The new session tokens.
    """
    raw_refresh = refresh_tokens.issue()
    expires_at = clock.now() + refresh_ttl
    await uow.refresh_tokens.add(
        StoredRefreshToken(
            token_hash=refresh_tokens.hash(raw_refresh),
            user_id=user_id,
            expires_at=expires_at,
        )
    )
    await uow.commit()
    return SessionTokens(
        access_token=access_tokens.issue(user_id),
        refresh_token=raw_refresh,
        refresh_expires_at=expires_at,
    )
