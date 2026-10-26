"""Expected failures of the learning domain."""


class DomainError(Exception):
    """Base class for failures the application knows how to explain."""


class InvalidEmail(DomainError):
    """Raised when an email address cannot be accepted."""


class WeakPassword(DomainError):
    """Raised when a password does not meet the strength policy."""


class EmailAlreadyRegistered(DomainError):
    """Raised when an account already uses this email."""


class InvalidCredentials(DomainError):
    """Raised when an email and password do not match an account."""


class InvalidToken(DomainError):
    """Raised when a session token is missing, expired, or forged."""
