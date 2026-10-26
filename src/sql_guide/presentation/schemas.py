"""HTTP response models."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness payload returned by the API."""

    status: str
