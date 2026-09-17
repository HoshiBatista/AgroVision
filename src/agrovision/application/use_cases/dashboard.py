"""Use case: aggregate live stream metrics for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass

from agrovision.application.ports import FrameBusPort
from agrovision.domain.stream import StreamMetrics, StreamStatus


@dataclass(frozen=True, slots=True)
class DashboardState:
    """Aggregate dashboard state derived from per-stream metrics."""

    total_sheep: int
    active_streams: int
    streams: tuple[StreamMetrics, ...]


class BuildDashboard:
    """Builds an aggregate dashboard snapshot from the frame bus."""

    def __init__(self, bus: FrameBusPort) -> None:
        self._bus = bus

    def execute(self) -> DashboardState:
        """Return the current aggregate dashboard state."""
        metrics = self._bus.metrics()
        running = [m for m in metrics if m.status == StreamStatus.RUNNING]
        total_sheep = sum(m.sheep_count for m in running)
        return DashboardState(
            total_sheep=total_sheep,
            active_streams=len(running),
            streams=tuple(metrics),
        )
