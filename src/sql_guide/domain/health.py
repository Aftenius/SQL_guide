"""Liveness of the application process."""

from dataclasses import dataclass
from enum import StrEnum


class ServiceStatus(StrEnum):
    """Whether the process can answer requests."""

    OK = "ok"


@dataclass(frozen=True, slots=True)
class HealthStatus:
    """Result of a liveness check.

    Attributes:
        status: Process liveness. This check does not inspect the database.
    """

    status: ServiceStatus
