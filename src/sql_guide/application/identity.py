"""Commands and results for registration and sessions."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegisterCommand:
    """Data needed to open an account.

    Attributes:
        email: Address the learner typed.
        password: Plain password. It is hashed before storage.
    """

    email: str
    password: str


@dataclass(frozen=True, slots=True)
class LoginCommand:
    """Data needed to open a session.

    Attributes:
        email: Address the learner typed.
        password: Plain password.
    """

    email: str
    password: str


@dataclass(frozen=True, slots=True)
class LearnerView:
    """Account and progress root returned to the client.

    Attributes:
        id: Account id.
        email: Normalized email.
        profile_created_at: When progress tracking started for this account.
    """

    id: UUID
    email: str
    profile_created_at: datetime


@dataclass(frozen=True, slots=True)
class SessionTokens:
    """Tokens issued for one successful authentication.

    Attributes:
        access_token: Short-lived bearer token.
        refresh_token: Opaque token stored only in an httpOnly cookie.
        refresh_expires_at: Expiry of the refresh token.
    """

    access_token: str
    refresh_token: str
    refresh_expires_at: datetime
