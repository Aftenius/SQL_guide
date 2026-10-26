"""Translate domain failures into HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sql_guide.domain.errors import (
    DomainError,
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidEmail,
    InvalidToken,
    WeakPassword,
)

_MESSAGES: dict[type[DomainError], tuple[int, str]] = {
    InvalidEmail: (422, "Email address is invalid"),
    WeakPassword: (422, "Password must be at least 8 characters"),
    EmailAlreadyRegistered: (409, "Email is already registered"),
    InvalidCredentials: (401, "Invalid email or password"),
    InvalidToken: (401, "Invalid or expired session"),
}


def register_domain_errors(app: FastAPI) -> None:
    """Attach the handler that maps domain errors to status codes.

    Args:
        app: Application that should explain domain failures.
    """

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        status_code, message = _MESSAGES.get(
            type(exc),
            (400, "Request could not be completed"),
        )
        return JSONResponse(status_code=status_code, content={"detail": message})
