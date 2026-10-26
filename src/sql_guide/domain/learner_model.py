"""Stored model credentials for one learner."""

from dataclasses import dataclass
from datetime import datetime

from sql_guide.domain.user import UserId


@dataclass(frozen=True, slots=True)
class LearnerModel:
    """Encrypted model key belonging to an account.

    Attributes:
        user_id: Account that owns the key.
        provider: Provider slug.
        model: Model name.
        ciphertext: Encrypted API key.
        hint: Last four characters of the key.
        updated_at: Moment the key or model was saved.
    """

    user_id: UserId
    provider: str
    model: str
    ciphertext: str
    hint: str
    updated_at: datetime
