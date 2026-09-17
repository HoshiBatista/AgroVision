"""Use case: detect and count sheep in a single image."""

from __future__ import annotations

import time
from dataclasses import dataclass

from agrovision.application.ports import DetectorPort, Image
from agrovision.domain.counting import FrameResult
from agrovision.domain.detection import Detection
from agrovision.domain.model import ModelMetadata


@dataclass(frozen=True, slots=True)
class ImageDetectionResult:
    """The result of running image detection, with timing and model metadata."""

    frame: FrameResult
    processing_ms: float
    model: ModelMetadata

    @property
    def count(self) -> int:
        """Number of detected sheep."""
        return self.frame.count_above(self.model.confidence_threshold)

    @property
    def uncertain(self) -> tuple[Detection, ...]:
        """Detections below the model's confidence threshold."""
        return self.frame.uncertain(self.model.confidence_threshold)


class DetectImageUseCase:
    """Runs the detector on one image and wraps the result with metadata."""

    def __init__(self, detector: DetectorPort) -> None:
        self._detector = detector

    def execute(self, image: Image) -> ImageDetectionResult:
        """Detect sheep in the given BGR image array."""
        started = time.perf_counter()
        frame = self._detector.detect(image)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return ImageDetectionResult(
            frame=frame,
            processing_ms=elapsed_ms,
            model=self._detector.metadata,
        )
