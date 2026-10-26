"""Refresh-token record stored for an account."""

from dataclasses import dataclass
from datetime import datetime

from sql_guide.domain.user import UserId


@dataclass(frozen=True, slots=True)
class StoredRefreshToken:
    """Hashed refresh token that can be revoked.

    Attributes:
        token_hash: SHA-256 hex digest of the opaque token.
        user_id: Account that owns the session.
        expires_at: Moment after which the token must be rejected.
    """

    token_hash: str
    user_id: UserId
    expires_at: datetime
