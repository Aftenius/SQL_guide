"""Store solved days and SM-2 review cards.

Revision ID: 0003_practice_calendar
Revises: 0002_yandex_identity
Create Date: 2026-10-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_practice_calendar"
down_revision: str | None = "0002_yandex_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the practice calendar tables."""
    op.create_table(
        "practice_days",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("practiced_on", sa.Date(), nullable=False),
        sa.Column("solved_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "practiced_on"),
    )
    op.create_table(
        "review_cards",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("track_slug", sa.String(length=64), nullable=False),
        sa.Column("lesson_slug", sa.String(length=64), nullable=False),
        sa.Column("ease", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False),
        sa.Column("repetitions", sa.Integer(), nullable=False),
        sa.Column("due_on", sa.Date(), nullable=False),
        sa.Column("last_reviewed_on", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "track_slug", "lesson_slug"),
    )


def downgrade() -> None:
    """Drop the practice calendar tables."""
    op.drop_table("review_cards")
    op.drop_table("practice_days")
