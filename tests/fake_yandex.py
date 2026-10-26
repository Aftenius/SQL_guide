"""Yandex client that returns accounts chosen by a test."""

from sql_guide.domain.errors import YandexSignInFailed
from sql_guide.domain.yandex import YandexAccount


class FakeYandexClient:
    """In-memory Yandex client keyed by authorization code."""

    def __init__(self) -> None:
        """Start with no codes accepted."""
        self.accounts: dict[str, YandexAccount] = {}

    def authorization_url(self, state: str) -> str:
        """Return a URL that echoes the state."""
        return f"https://oauth.yandex.ru/authorize?state={state}"

    async def exchange(self, code: str) -> YandexAccount:
        """Return the account registered for the code.

        Args:
            code: Authorization code the test prepared.

        Returns:
            The account for that code.

        Raises:
            YandexSignInFailed: The code was not prepared.
        """
        account = self.accounts.get(code)
        if account is None:
            raise YandexSignInFailed
        return account
