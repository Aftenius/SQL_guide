"""HTTP request and response models."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness payload returned by the API."""

    status: str


class CredentialsRequest(BaseModel):
    """Email and password submitted by a learner."""

    email: str
    password: str


class LearnerResponse(BaseModel):
    """Account and progress root returned after registration or session lookup."""

    id: UUID
    email: str
    profile_created_at: datetime


class AccessTokenResponse(BaseModel):
    """Bearer token returned by login and refresh."""

    access_token: str
    token_type: str = "bearer"


class AuthorizationUrlResponse(BaseModel):
    """Browser URL that starts Yandex sign-in."""

    authorization_url: str


class SolveRequest(BaseModel):
    """Lesson step the learner marked as solved."""

    track: str
    lesson: str


class SolveResponse(BaseModel):
    """Next review after a solve."""

    track: str
    lesson: str
    due_on: date
    interval_days: int
    counted: bool
    today: date


class SolvedDayResponse(BaseModel):
    """One calendar day that contains solved steps."""

    date: date
    solved: int


class ReviewResponse(BaseModel):
    """Scheduled repetition of one step."""

    track: str
    lesson: str
    due_on: date
    interval_days: int


class LearnerModelResponse(BaseModel):
    """Saved model shown in the profile. The API key is not included."""

    configured: bool
    provider: str | None = None
    model: str | None = None
    hint: str | None = None
    updated_at: datetime | None = None


class SaveLearnerModelRequest(BaseModel):
    """Model choice and an optional replacement key."""

    provider: str
    model: str
    api_key: str = ""


class CheckLearnerModelRequest(BaseModel):
    """Key to try against the provider."""

    provider: str
    model: str
    api_key: str = ""


class QueryRequest(BaseModel):
    """Learner statement and the practice database it should see."""

    database: str
    sql: str


class QueryResponse(BaseModel):
    """Rows returned by one learner statement."""

    columns: list[str]
    rows: list[list[str | int | float | bool | None]]


class PracticeCalendarResponse(BaseModel):
    """Solved days and scheduled reviews for the profile."""

    today: date
    streak: int
    days: list[SolvedDayResponse]
    reviews: list[ReviewResponse]
