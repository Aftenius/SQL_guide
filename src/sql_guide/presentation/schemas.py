"""HTTP request and response models."""

from datetime import datetime
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
