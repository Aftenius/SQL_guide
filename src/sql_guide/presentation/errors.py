"""Translate domain failures into HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sql_guide.domain.errors import (
    DomainError,
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidEmail,
    InvalidLessonKey,
    InvalidModelChoice,
    InvalidModelKey,
    InvalidOAuthState,
    InvalidToken,
    ModelCheckFailed,
    ModelKeyUnreadable,
    SandboxQueryFailed,
    SandboxSetupFailed,
    UnknownPracticeDatabase,
    UnsafeSql,
    WeakPassword,
    YandexSignInFailed,
)

_MESSAGES: dict[type[DomainError], tuple[int, str]] = {
    InvalidEmail: (422, "Email address is invalid"),
    InvalidLessonKey: (422, "Lesson key is invalid"),
    UnknownPracticeDatabase: (422, "Unknown practice database"),
    SandboxSetupFailed: (500, "Practice tables could not be prepared"),
    InvalidModelChoice: (422, "Model choice is invalid"),
    InvalidModelKey: (422, "API key is invalid"),
    ModelKeyUnreadable: (409, "Saved API key cannot be read"),
    ModelCheckFailed: (400, "Model API rejected the key"),
    WeakPassword: (422, "Password must be at least 8 characters"),
    EmailAlreadyRegistered: (409, "Email is already registered"),
    InvalidCredentials: (401, "Invalid email or password"),
    InvalidToken: (401, "Invalid or expired session"),
    InvalidOAuthState: (401, "Yandex sign-in could not be confirmed"),
    YandexSignInFailed: (401, "Yandex sign-in failed"),
}

_UNSAFE = {
    "This statement is not allowed": (
        "Такая команда здесь не выполняется. Нужна одна команда "
        "SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER или DROP."
    ),
    "Only one statement is allowed": "Можно отправить только одну команду.",
    "A statement is required": "Сначала напишите запрос.",
}


def _sql_detail(exc: DomainError) -> tuple[int, str]:
    """Return the status and the text safe to show for one domain error."""
    if isinstance(exc, UnsafeSql):
        return 400, _UNSAFE.get(str(exc), "Такая команда здесь не выполняется.")
    if isinstance(exc, SandboxQueryFailed):
        return 400, str(exc)
    status_code, message = _MESSAGES.get(
        type(exc),
        (400, "Request could not be completed"),
    )
    return status_code, message


def register_domain_errors(app: FastAPI) -> None:
    """Attach the handler that maps domain errors to status codes.

    Args:
        app: Application that should explain domain failures.
    """

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        status_code, message = _sql_detail(exc)
        return JSONResponse(status_code=status_code, content={"detail": message})
