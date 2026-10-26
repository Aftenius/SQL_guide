"""Registration and session routes."""

import secrets
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sql_guide.application.identity import LearnerView, LoginCommand, RegisterCommand
from sql_guide.domain.errors import InvalidOAuthState, InvalidToken
from sql_guide.infrastructure.config import Settings
from sql_guide.infrastructure.container import AppContainer
from sql_guide.presentation.schemas import (
    AccessTokenResponse,
    AuthorizationUrlResponse,
    CredentialsRequest,
    LearnerResponse,
)

REFRESH_COOKIE = "refresh_token"
STATE_COOKIE = "oauth_state"
_COOKIE_PATH = "/auth"
_YANDEX_COOKIE_PATH = "/auth/yandex"
_bearer = HTTPBearer(auto_error=False)


def _learner_response(learner: LearnerView) -> LearnerResponse:
    return LearnerResponse(
        id=learner.id,
        email=learner.email,
        profile_created_at=learner.profile_created_at,
    )


def _set_refresh_cookie(
    response: Response,
    token: str,
    expires_at: datetime,
    settings: Settings,
) -> None:
    remaining = int((expires_at - datetime.now(UTC)).total_seconds())
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=max(remaining, 0),
        path=_COOKIE_PATH,
    )


def create_auth_router(container: AppContainer) -> APIRouter:
    """Build registration and session routes.

    Args:
        container: Use cases and cookie settings.

    Returns:
        A router mounted at the application root.
    """
    router = APIRouter()

    @router.post("/auth/register", response_model=LearnerResponse, status_code=201)
    async def register(body: CredentialsRequest) -> LearnerResponse:
        """Create an account and its progress root."""
        learner = await container.register_user.execute(
            RegisterCommand(email=body.email, password=body.password)
        )
        return _learner_response(learner)

    @router.post("/auth/login", response_model=AccessTokenResponse)
    async def login(
        body: CredentialsRequest,
        response: Response,
    ) -> AccessTokenResponse:
        """Check a password and set the refresh cookie."""
        session = await container.login_user.execute(
            LoginCommand(email=body.email, password=body.password)
        )
        _set_refresh_cookie(
            response,
            session.refresh_token,
            session.refresh_expires_at,
            container.settings,
        )
        return AccessTokenResponse(access_token=session.access_token)

    @router.post("/auth/refresh", response_model=AccessTokenResponse)
    async def refresh(
        response: Response,
        refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
    ) -> AccessTokenResponse:
        """Rotate the refresh cookie and return a new access token."""
        if refresh_token is None:
            raise InvalidToken
        session = await container.refresh_session.execute(refresh_token)
        _set_refresh_cookie(
            response,
            session.refresh_token,
            session.refresh_expires_at,
            container.settings,
        )
        return AccessTokenResponse(access_token=session.access_token)

    @router.post("/auth/logout", status_code=204)
    async def logout(
        response: Response,
        refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
    ) -> Response:
        """Revoke the refresh token and clear the cookie."""
        await container.logout_user.execute(refresh_token)
        response.delete_cookie(REFRESH_COOKIE, path=_COOKIE_PATH)
        return Response(status_code=204)

    @router.get("/auth/yandex/start", response_model=AuthorizationUrlResponse)
    def start_yandex(response: Response) -> AuthorizationUrlResponse:
        """Return the Yandex URL and remember the state cookie."""
        state = secrets.token_urlsafe(32)
        response.set_cookie(
            key=STATE_COOKIE,
            value=state,
            httponly=True,
            secure=container.settings.cookie_secure,
            samesite="lax",
            max_age=600,
            path=_YANDEX_COOKIE_PATH,
        )
        return AuthorizationUrlResponse(
            authorization_url=container.yandex.authorization_url(state)
        )

    @router.get("/auth/yandex/callback", response_model=AccessTokenResponse)
    async def yandex_callback(
        response: Response,
        code: str | None = None,
        state: str | None = None,
        oauth_state: Annotated[str | None, Cookie(alias=STATE_COOKIE)] = None,
    ) -> AccessTokenResponse:
        """Finish Yandex sign-in and set the refresh cookie."""
        if code is None or state is None or oauth_state is None or state != oauth_state:
            raise InvalidOAuthState
        session = await container.sign_in_with_yandex.execute(code)
        _set_refresh_cookie(
            response,
            session.refresh_token,
            session.refresh_expires_at,
            container.settings,
        )
        response.delete_cookie(STATE_COOKIE, path=_YANDEX_COOKIE_PATH)
        return AccessTokenResponse(access_token=session.access_token)

    async def bearer_token(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    ) -> str:
        """Read the bearer token or reject the request."""
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        return credentials.credentials

    @router.get("/me", response_model=LearnerResponse)
    async def me(token: Annotated[str, Depends(bearer_token)]) -> LearnerResponse:
        """Return the account and progress root for the bearer token."""
        learner = await container.get_current_learner.execute(token)
        return _learner_response(learner)

    return router
