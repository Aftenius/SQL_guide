"""Learning progress root attached to an account."""

from dataclasses import dataclass
from datetime import datetime

from sql_guide.domain.user import UserId


@dataclass(frozen=True, slots=True)
class LearnerProfile:
    """Progress anchor created together with the account.

    Cards and attempts will hang off this profile. The profile exists so a
    new account already has a place to store progress.

    Attributes:
        user_id: Owner of the progress.
        created_at: Moment the progress record was created.
    """

    user_id: UserId
    created_at: datetime
