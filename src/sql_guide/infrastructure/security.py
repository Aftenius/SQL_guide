"""Password hashing and session tokens."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import bcrypt
import jwt

from sql_guide.domain.errors import InvalidToken
from sql_guide.domain.ports import Clock
from sql_guide.domain.user import UserId

_JWT_ALGORITHM = "HS256"


class SystemClock:
    """Clock that reads the operating system time."""

    def now(self) -> datetime:
        """Return the current UTC time.

        Returns:
            A timezone-aware instant.
        """
        return datetime.now(UTC)


class UuidIdGenerator:
    """Identifier source backed by UUID4."""

    def new_id(self) -> UUID:
        """Return a new random identifier.

        Returns:
            A UUID4 value.
        """
        return uuid4()


class BcryptPasswordHasher:
    """bcrypt password hasher."""

    def __init__(self, rounds: int) -> None:
        """Store the bcrypt cost.

        Args:
            rounds: bcrypt cost factor. Tests use a small value.
        """
        self._rounds = rounds

    def hash(self, password: str) -> str:
        """Hash a plain password.

        Args:
            password: Password to store.

        Returns:
            The bcrypt hash as ASCII text.
        """
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=self._rounds))
        return hashed.decode()

    def verify(self, password: str, password_hash: str) -> bool:
        """Check a plain password against a stored hash.

        Args:
            password: Password from the login form.
            password_hash: Hash stored on the account.

        Returns:
            True when the password matches.
        """
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except ValueError:
            return False


class JwtAccessTokenIssuer:
    """HS256 access tokens."""

    def __init__(self, secret: str, ttl_minutes: int, clock: Clock) -> None:
        """Store the signing secret and lifetime.

        Args:
            secret: HMAC secret.
            ttl_minutes: Lifetime of each issued token.
            clock: Clock used for the expiry claim.
        """
        self._secret = secret
        self._ttl = timedelta(minutes=ttl_minutes)
        self._clock = clock

    def issue(self, user_id: UserId) -> str:
        """Create an access token.

        Args:
            user_id: Account that will be read back from the token.

        Returns:
            A compact JWT.
        """
        payload = {
            "sub": str(user_id.value),
            "exp": self._clock.now() + self._ttl,
            "type": "access",
        }
        token = jwt.encode(payload, self._secret, algorithm=_JWT_ALGORITHM)
        return str(token)

    def read(self, token: str) -> UserId:
        """Read the account id from an access token.

        Args:
            token: Compact JWT from the Authorization header.

        Returns:
            The account id stored in the subject claim.

        Raises:
            InvalidToken: The token is expired, forged, or the wrong type.
        """
        try:
            payload = jwt.decode(token, self._secret, algorithms=[_JWT_ALGORITHM])
        except jwt.PyJWTError as exc:
            raise InvalidToken from exc
        if payload.get("type") != "access":
            raise InvalidToken
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise InvalidToken
        try:
            return UserId(UUID(subject))
        except ValueError as exc:
            raise InvalidToken from exc


class SecretRefreshTokenFactory:
    """Random refresh tokens stored only as a SHA-256 digest."""

    def issue(self) -> str:
        """Create an opaque refresh token.

        Returns:
            A URL-safe random token.
        """
        return secrets.token_urlsafe(32)

    def hash(self, token: str) -> str:
        """Digest a refresh token for storage.

        Args:
            token: Opaque token from the cookie.

        Returns:
            A hex SHA-256 digest.
        """
        return hashlib.sha256(token.encode()).hexdigest()
