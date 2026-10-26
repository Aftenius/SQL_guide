"""Relational tables for accounts, progress, and refresh tokens."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for application tables."""


class UserModel(Base):
    """Account row."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class LearnerProfileModel(Base):
    """Progress root row, one per account."""

    __tablename__ = "learner_profiles"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class RefreshTokenModel(Base):
    """Digest of a refresh token."""

    __tablename__ = "refresh_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class PracticeDayModel(Base):
    """Solved-step count for one account on one calendar day."""

    __tablename__ = "practice_days"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    practiced_on: Mapped[date] = mapped_column(Date, primary_key=True)
    solved_count: Mapped[int] = mapped_column(Integer, nullable=False)


class ReviewCardModel(Base):
    """SM-2 card for one lesson step."""

    __tablename__ = "review_cards"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    track_slug: Mapped[str] = mapped_column(String(64), primary_key=True)
    lesson_slug: Mapped[str] = mapped_column(String(64), primary_key=True)
    ease: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, nullable=False)
    due_on: Mapped[date] = mapped_column(Date, nullable=False)
    last_reviewed_on: Mapped[date] = mapped_column(Date, nullable=False)


class LearnerModelRow(Base):
    """Encrypted model key for one account."""

    __tablename__ = "learner_models"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[str] = mapped_column(String(8), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class ExternalIdentityModel(Base):
    """Provider subject linked to an account."""

    __tablename__ = "external_identities"

    provider: Mapped[str] = mapped_column(String(32), primary_key=True)
    subject: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
