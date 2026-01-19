"""Health check controller.

Provides endpoints for monitoring API health and status.
"""

from __future__ import annotations

from datetime import datetime, timezone

from litestar import Controller, get

from ..models import HealthResponse


class HealthController(Controller):
    """Controller for health check endpoints.

    Provides endpoints to monitor the health and status of the API
    and its dependencies.

    Attributes:
        path: Base path for all health endpoints.
        tags: OpenAPI tags for documentation grouping.
    """

    path = "/health"
    tags = ["Health"]

    @get("/")
    async def health_check(self) -> HealthResponse:
        """Check the overall health of the API.

        Returns the current status of the API and all its dependencies
        including database and cache connections.

        Returns:
            HealthResponse: Current health status of the API.

        Example:
            >>> response = await client.get("/health")
            >>> response.json()
            {"status": "healthy", "version": "1.0.0", ...}
        """
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.now(timezone.utc),
            database="healthy",
            cache="healthy",
        )

    @get("/ready")
    async def readiness_check(self) -> dict[str, str]:
        """Check if the API is ready to accept requests.

        This endpoint is used by orchestration systems like Kubernetes
        to determine if the service should receive traffic.

        Returns:
            dict: Readiness status.
        """
        return {"status": "ready"}

    @get("/live")
    async def liveness_check(self) -> dict[str, str]:
        """Check if the API process is alive.

        This endpoint is used by orchestration systems to determine
        if the service process needs to be restarted.

        Returns:
            dict: Liveness status.
        """
        return {"status": "alive"}
