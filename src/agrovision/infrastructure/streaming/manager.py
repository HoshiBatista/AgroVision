"""Owns the frame bus and per-stream inference worker threads."""

from __future__ import annotations

import logging
import threading

from agrovision.application.ports import DetectorPort, FrameBusPort, StreamSourcePort
from agrovision.config import Settings
from agrovision.domain.stream import StreamSource
from agrovision.infrastructure.streaming.config import load_stream_sources, startable_sources
from agrovision.infrastructure.streaming.file_source import FileStreamSource
from agrovision.infrastructure.streaming.frame_bus import InMemoryFrameBus
from agrovision.infrastructure.streaming.rtsp_source import RtspStreamSource
from agrovision.infrastructure.streaming.worker import StreamWorker

logger = logging.getLogger("agrovision.streaming")


class StreamManager:
    """Starts and stops inference workers and exposes the shared frame bus."""

    def __init__(
        self,
        sources: list[StreamSource],
        detector: DetectorPort,
        settings: Settings,
        bus: InMemoryFrameBus | None = None,
    ) -> None:
        self._sources = sources
        self._detector = detector
        self._settings = settings
        self._bus = bus or InMemoryFrameBus()
        self._model_lock = threading.Lock()
        self._state_lock = threading.RLock()
        self._workers: dict[str, tuple[StreamWorker, threading.Event]] = {}
        self._running = False

    @property
    def bus(self) -> FrameBusPort:
        """The shared frame bus."""
        return self._bus

    def sources(self) -> list[StreamSource]:
        """Return the configured stream sources."""
        with self._state_lock:
            return list(self._sources)

    def latest_jpeg(self, stream_id: str) -> bytes | None:
        """Return the latest annotated JPEG for a stream, or None."""
        return self._bus.latest_jpeg(stream_id)

    def has_stream(self, stream_id: str) -> bool:
        """Return whether a stream with the given id is configured."""
        with self._state_lock:
            return any(source.id == stream_id for source in self._sources)

    def add_source(self, source: StreamSource) -> None:
        """Register a source and start it immediately when the manager is running."""
        with self._state_lock:
            if self.has_stream(source.id):
                raise ValueError(f"Stream id already exists: {source.id}")
            self._sources.append(source)
            if self._running:
                self._start_worker(source)

    def remove_source(self, stream_id: str) -> bool:
        """Remove a dynamic source and stop its worker."""
        with self._state_lock:
            source = next((item for item in self._sources if item.id == stream_id), None)
            if source is None or source.kind != "rtsp":
                return False
            self._sources.remove(source)
            worker_entry = self._workers.pop(stream_id, None)
        if worker_entry is not None:
            worker, stop_event = worker_entry
            stop_event.set()
            worker.join(timeout=2.0)
        self._bus.remove(stream_id)
        return True

    def start(self) -> None:
        """Start one worker thread per configured stream."""
        with self._state_lock:
            if self._running:
                return
            self._running = True
            for source in self._sources:
                self._start_worker(source)
            logger.info("Started %d stream workers", len(self._workers))

    def _start_worker(self, source: StreamSource) -> None:
        adapter: StreamSourcePort
        if source.kind == "rtsp":
            adapter = RtspStreamSource(
                source,
                self._settings.rtsp_open_timeout_ms,
                self._settings.rtsp_read_timeout_ms,
            )
        else:
            adapter = FileStreamSource(source)
        stop_event = threading.Event()
        worker = StreamWorker(
            adapter,
            self._detector,
            self._bus,
            self._model_lock,
            self._settings,
            stop_event,
        )
        self._workers[source.id] = (worker, stop_event)
        worker.start()

    def stop(self) -> None:
        """Signal all workers to stop and wait briefly for them to finish."""
        with self._state_lock:
            entries = list(self._workers.values())
            self._workers.clear()
            self._running = False
        for _, stop_event in entries:
            stop_event.set()
        for worker, _ in entries:
            worker.join(timeout=2.0)


def build_stream_manager(settings: Settings, detector: DetectorPort) -> StreamManager:
    """Construct a stream manager from the configured, openable sources."""
    configured = load_stream_sources(settings.streams_config_path)
    sources = startable_sources(configured)
    if len(sources) < len(configured):
        logger.warning("Skipping %d stream(s) with missing files", len(configured) - len(sources))
    return StreamManager(sources, detector, settings)
