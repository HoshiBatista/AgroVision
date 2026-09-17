"""Bounded single-worker queue for safe detector access from API and streams."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from threading import BoundedSemaphore

from agrovision.application.errors import InferenceBusyError, InferenceTimeoutError
from agrovision.application.ports import DetectorPort, Image
from agrovision.domain.counting import FrameResult
from agrovision.domain.model import ModelMetadata


class QueuedDetector:
    """Serialize detector calls and apply queue and execution deadlines.

    Ultralytics models are mutable and are not guaranteed to be safe when the API
    and background stream workers call the same instance concurrently. A single
    executor worker provides one ordered inference path for every caller.
    """

    def __init__(
        self,
        detector: DetectorPort,
        *,
        capacity: int,
        queue_wait_seconds: float,
        inference_timeout_seconds: float,
    ) -> None:
        self._detector = detector
        self._slots = BoundedSemaphore(capacity)
        self._queue_wait_seconds = queue_wait_seconds
        self._inference_timeout_seconds = inference_timeout_seconds
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="model-inference")

    @property
    def metadata(self) -> ModelMetadata:
        return self._detector.metadata

    def detect(self, image: Image) -> FrameResult:
        """Submit one frame to the bounded queue and wait for its result."""
        if not self._slots.acquire(timeout=self._queue_wait_seconds):
            raise InferenceBusyError("The model queue is full; retry shortly")
        try:
            future = self._executor.submit(self._detector.detect, image)
        except BaseException:
            self._slots.release()
            raise
        future.add_done_callback(lambda _: self._slots.release())
        try:
            return future.result(timeout=self._inference_timeout_seconds)
        except FutureTimeoutError as exc:
            future.cancel()
            raise InferenceTimeoutError("Model inference exceeded its deadline") from exc

    def set_confidence_threshold(self, threshold: float) -> None:
        """Update the wrapped detector threshold through its runtime control."""
        setter = getattr(self._detector, "set_confidence_threshold", None)
        if not callable(setter):
            raise RuntimeError("The active detector does not support runtime threshold updates")
        setter(threshold)

    def close(self) -> None:
        """Stop accepting work and release the inference worker."""
        self._executor.shutdown(wait=True, cancel_futures=True)
