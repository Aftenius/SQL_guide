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


class InvalidOAuthState(DomainError):
    """Raised when the Yandex callback state does not match the cookie."""


class YandexSignInFailed(DomainError):
    """Raised when Yandex does not return a usable account."""


class UnsafeSql(DomainError):
    """Raised when a statement is outside the sandbox policy."""


class SandboxQueryFailed(DomainError):
    """Raised when a safe statement is rejected by the database."""


class SandboxSetupFailed(DomainError):
    """Raised when trusted setup SQL cannot be applied."""


class InvalidLessonKey(DomainError):
    """Raised when a track or lesson slug cannot be stored."""


class InvalidModelChoice(DomainError):
    """Raised when the provider and model are not in the catalog."""


class InvalidModelKey(DomainError):
    """Raised when an API key is missing or not a token."""


class ModelKeyUnreadable(DomainError):
    """Raised when a stored API key cannot be decrypted."""


class ModelCheckFailed(DomainError):
    """Raised when the provider rejects the key or cannot be reached."""
