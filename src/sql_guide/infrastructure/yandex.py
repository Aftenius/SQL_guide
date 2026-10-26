"""Yandex ID authorization-code client."""

from urllib.parse import urlencode

import httpx

from sql_guide.domain.errors import YandexSignInFailed
from sql_guide.domain.yandex import YandexAccount

_AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
_TOKEN_URL = "https://oauth.yandex.ru/token"
_INFO_URL = "https://login.yandex.ru/info"


class HttpxYandexClient:
    """Yandex ID client backed by HTTP."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        """Store the application credentials.

        Args:
            client_id: Yandex OAuth client id.
            client_secret: Yandex OAuth client secret.
            redirect_uri: Callback URL registered for the application.
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

    def authorization_url(self, state: str) -> str:
        """Build the browser URL that starts sign-in.

        Args:
            state: Random value the callback must echo back.

        Returns:
            The Yandex authorization URL.
        """
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "state": state,
                "scope": "login:email",
            }
        )
        return f"{_AUTHORIZE_URL}?{query}"

    async def exchange(self, code: str) -> YandexAccount:
        """Trade an authorization code for the Yandex account.

        Args:
            code: Code from the Yandex redirect.

        Returns:
            The stable id and confirmed email.

        Raises:
            YandexSignInFailed: Yandex rejected the code or omitted the email.
        """
        async with httpx.AsyncClient(timeout=10) as client:
            token_response = await client.post(
                _TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )
            if token_response.status_code != 200:
                raise YandexSignInFailed
            token_payload = token_response.json()
            if not isinstance(token_payload, dict):
                raise YandexSignInFailed
            access_token = token_payload.get("access_token")
            if not isinstance(access_token, str):
                raise YandexSignInFailed
            info_response = await client.get(
                _INFO_URL,
                params={"format": "json"},
                headers={"Authorization": f"OAuth {access_token}"},
            )
            if info_response.status_code != 200:
                raise YandexSignInFailed
            payload = info_response.json()
        if not isinstance(payload, dict):
            raise YandexSignInFailed
        subject = payload.get("id")
        email = payload.get("default_email")
        if not isinstance(subject, str) or not isinstance(email, str) or email == "":
            raise YandexSignInFailed
        return YandexAccount(subject=subject, email=email)
