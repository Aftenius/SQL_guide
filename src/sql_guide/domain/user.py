"""Account identity."""

import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sql_guide.domain.errors import InvalidEmail, WeakPassword

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True, slots=True)
class UserId:
    """Identity of an account."""

    value: UUID


@dataclass(frozen=True, slots=True)
class Email:
    """Normalized email address.

    Attributes:
        value: Lower-case address without surrounding space.
    """

    value: str

    @classmethod
    def parse(cls, raw: str) -> "Email":
        """Validate and normalize an email address.

        Args:
            raw: Address as the learner typed it.

        Returns:
            The normalized email.

        Raises:
            InvalidEmail: The address is empty or malformed.
        """
        normalized = raw.strip().lower()
        if _EMAIL_PATTERN.fullmatch(normalized) is None:
            raise InvalidEmail
        return cls(normalized)


def require_strong_password(password: str) -> None:
    """Reject passwords that are too short to store.

    Args:
        password: Plain password from the registration form.

    Raises:
        WeakPassword: The password is shorter than 8 characters.
    """
    if len(password) < _MIN_PASSWORD_LENGTH:
        raise WeakPassword


@dataclass(frozen=True, slots=True)
class User:
    """Registered learner account.

    Attributes:
        id: Stable account id.
        email: Login name.
        password_hash: One-way hash. The plain password is never stored.
        created_at: Moment the account was created.
    """

    id: UserId
    email: Email
    password_hash: str
    created_at: datetime
