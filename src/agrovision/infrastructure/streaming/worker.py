"""Background inference worker that publishes annotated frames for one stream."""

from __future__ import annotations

import logging
import threading
import time

from agrovision.application.ports import DetectorPort, FrameBusPort, Image, StreamSourcePort
from agrovision.config import Settings
from agrovision.domain.stream import StreamMetrics, StreamStatus
from agrovision.infrastructure.imaging import annotate, encode_jpeg

logger = logging.getLogger("agrovision.streaming")


class StreamWorker(threading.Thread):
    """Reads frames from a source, runs detection, and publishes to the frame bus.

    A shared ``model_lock`` serialises access to the single detector, which is not
    guaranteed to be thread-safe across concurrent streams.
    """

    def __init__(
        self,
        source: StreamSourcePort,
        detector: DetectorPort,
        bus: FrameBusPort,
        model_lock: threading.Lock,
        settings: Settings,
        stop_event: threading.Event,
    ) -> None:
        super().__init__(name=f"stream-{source.source.id}", daemon=True)
        self._source = source
        self._detector = detector
        self._bus = bus
        self._model_lock = model_lock
        self._stride = max(1, settings.stream_frame_stride)
        self._quality = settings.stream_jpeg_quality
        self._interval = 1.0 / settings.stream_target_fps
        self._reconnect_seconds = settings.rtsp_reconnect_seconds
        self._stop_event = stop_event

    def run(self) -> None:
        """Process the stream until stopped or the source is exhausted."""
        stream_id = self._source.source.id
        index = 0
        while not self._stop_event.is_set():
            frames = self._source.frames()
            try:
                for frame in frames:
                    if self._stop_event.is_set():
                        break
                    if index % self._stride == 0:
                        self._process(stream_id, frame, index)
                        time.sleep(self._interval)
                    index += 1
            except Exception:  # keep one bad stream from crashing the process
                logger.exception("Stream %s failed", stream_id)
                self._publish_status(stream_id, StreamStatus.ERROR, index)
            finally:
                closer = getattr(frames, "close", None)
                if callable(closer):
                    closer()
            if self._stop_event.is_set():
                break
            if self._source.source.kind == "rtsp":
                self._publish_status(stream_id, StreamStatus.ERROR, index)
                self._stop_event.wait(self._reconnect_seconds)
                continue
            self._publish_status(stream_id, StreamStatus.STOPPED, index)
            break
            if self._source.source.kind != "rtsp" or self._stop_event.is_set():
                break
            self._publish_status(stream_id, StreamStatus.ERROR, index)
            self._stop_event.wait(self._reconnect_seconds)
        if not self._stop_event.is_set():
            self._publish_status(stream_id, StreamStatus.STOPPED, index)

    def _process(self, stream_id: str, frame: Image, index: int) -> None:
        started = time.perf_counter()
        with self._model_lock:
            result = self._detector.detect(frame)
        latency_ms = (time.perf_counter() - started) * 1000.0
        threshold = self._detector.metadata.confidence_threshold
        annotated = annotate(result, frame, threshold)
        jpeg = encode_jpeg(annotated, self._quality)
        metrics = StreamMetrics(
            stream_id=stream_id,
            status=StreamStatus.RUNNING,
            sheep_count=result.count_above(threshold),
            mean_confidence=result.mean_confidence,
            latency_ms=latency_ms,
            frame_index=index,
        )
        self._bus.publish(stream_id, jpeg, metrics)

    def _publish_status(self, stream_id: str, status: StreamStatus, index: int) -> None:
        self._bus.update_metrics(
            StreamMetrics(
                stream_id=stream_id,
                status=status,
                sheep_count=0,
                mean_confidence=0.0,
                latency_ms=0.0,
                frame_index=index,
            )
        )
