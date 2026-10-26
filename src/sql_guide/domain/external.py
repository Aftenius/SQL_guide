"""Link between an account and an external sign-in provider."""

from dataclasses import dataclass

from sql_guide.domain.user import UserId

YANDEX = "yandex"


@dataclass(frozen=True, slots=True)
class ExternalIdentity:
    """Stable provider subject attached to one account.

    Attributes:
        provider: Provider name, such as ``yandex``.
        subject: Provider's stable user id.
        user_id: Account that owns this sign-in.
    """

    provider: str
    subject: str
    user_id: UserId
