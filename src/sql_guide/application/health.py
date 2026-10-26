"""Report that the API process is alive."""

from sql_guide.domain.health import HealthStatus, ServiceStatus


class GetHealthStatus:
    """Return a liveness result without touching infrastructure."""

    def execute(self) -> HealthStatus:
        """Report that the process is alive.

        Returns:
            A status that only means the process answered. Database readiness
            is a separate check.
        """
        return HealthStatus(status=ServiceStatus.OK)
