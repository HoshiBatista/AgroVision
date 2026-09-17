"""Thread-safe in-memory frame bus implementing FrameBusPort."""

from __future__ import annotations

import threading

from agrovision.domain.stream import StreamMetrics


class InMemoryFrameBus:
    """Holds the latest annotated JPEG and metrics for each stream."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jpeg: dict[str, bytes] = {}
        self._metrics: dict[str, StreamMetrics] = {}

    def publish(self, stream_id: str, jpeg: bytes, metrics: StreamMetrics) -> None:
        """Publish the latest annotated JPEG and metrics for a stream."""
        with self._lock:
            self._jpeg[stream_id] = jpeg
            self._metrics[stream_id] = metrics

    def update_metrics(self, metrics: StreamMetrics) -> None:
        """Publish metrics only (e.g. a status change) without a new frame."""
        with self._lock:
            self._metrics[metrics.stream_id] = metrics

    def latest_jpeg(self, stream_id: str) -> bytes | None:
        """Return the latest annotated JPEG for a stream, or None."""
        with self._lock:
            return self._jpeg.get(stream_id)

    def metrics(self) -> list[StreamMetrics]:
        """Return the latest metrics for all known streams."""
        with self._lock:
            return list(self._metrics.values())

    def remove(self, stream_id: str) -> None:
        """Discard the cached frame and metrics for a removed stream."""
        with self._lock:
            self._jpeg.pop(stream_id, None)
            self._metrics.pop(stream_id, None)
