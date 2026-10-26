"""Port for the Yandex ID authorization-code flow."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class YandexAccount:
    """Account facts returned by Yandex.

    Attributes:
        subject: Stable Yandex user id.
        email: Confirmed default email.
    """

    subject: str
    email: str


class YandexClient(Protocol):
    """Talks to Yandex ID."""

    def authorization_url(self, state: str) -> str:
        """Build the browser URL that starts sign-in.

        Args:
            state: Random value the callback must echo back.
        """
        ...

    async def exchange(self, code: str) -> YandexAccount:
        """Trade an authorization code for the Yandex account.

        Args:
            code: Code from the Yandex redirect.

        Raises:
            YandexSignInFailed: Yandex rejected the code or omitted the email.
        """
        ...
